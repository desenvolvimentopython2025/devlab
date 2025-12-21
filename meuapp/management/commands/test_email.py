# meuapp/management/commands/test_email.py
import socket
import smtplib
import ssl
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail, get_connection
import time


class Command(BaseCommand):
    help = 'Testa conexão SMTP e configurações de email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-send',
            action='store_true',
            help='Testar envio de email real'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=10,
            help='Timeout para testes (padrão: 10 segundos)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== TESTE DE CONFIGURAÇÃO DE EMAIL ==='))
        
        # Verificar configurações
        self.test_configurations()
        
        # Testar DNS e conectividade
        self.test_dns_and_connectivity(options['timeout'])
        
        # Testar autenticação SMTP
        self.test_smtp_authentication(options['timeout'])
        
        # Testar envio real (se solicitado)
        if options['test_send']:
            self.test_email_send(options['timeout'])
    
    def test_configurations(self):
        """Testa as configurações do Django"""
        self.stdout.write('\n1. VERIFICANDO CONFIGURAÇÕES:')
        
        configs = [
            ('EMAIL_BACKEND', settings.EMAIL_BACKEND),
            ('EMAIL_HOST', settings.EMAIL_HOST),
            ('EMAIL_PORT', settings.EMAIL_PORT),
            ('EMAIL_USE_TLS', settings.EMAIL_USE_TLS),
            ('EMAIL_USE_SSL', settings.EMAIL_USE_SSL),
            ('EMAIL_HOST_USER', settings.EMAIL_HOST_USER),
            ('EMAIL_HOST_PASSWORD', '***' if settings.EMAIL_HOST_PASSWORD else 'NÃO CONFIGURADA'),
            ('DEFAULT_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL),
            ('EMAIL_TIMEOUT', getattr(settings, 'EMAIL_TIMEOUT', 'Não definido')),
        ]
        
        for key, value in configs:
            self.stdout.write(f'  {key}: {value}')
        
        # Verificar inconsistências
        if settings.EMAIL_USE_TLS and settings.EMAIL_USE_SSL:
            self.stdout.write(self.style.ERROR('  ERRO: EMAIL_USE_TLS e EMAIL_USE_SSL são mutuamente exclusivos!'))
        elif not settings.EMAIL_USE_TLS and not settings.EMAIL_USE_SSL:
            self.stdout.write(self.style.WARNING('  AVISO: Nenhum protocolo de segurança definido (TLS ou SSL)'))
    
    def test_dns_and_connectivity(self, timeout):
        """Testa resolução DNS e conectividade básica"""
        self.stdout.write('\n2. TESTANDO DNS E CONECTIVIDADE:')
        
        try:
            # Testar resolução DNS
            self.stdout.write(f'  Resolvendo DNS para {settings.EMAIL_HOST}...')
            start_time = time.time()
            ip_address = socket.gethostbyname(settings.EMAIL_HOST)
            dns_time = time.time() - start_time
            self.stdout.write(f'  ✓ DNS resolvido: {settings.EMAIL_HOST} → {ip_address} ({dns_time:.2f}s)')
            
            # Testar conectividade na porta
            self.stdout.write(f'  Testando conexão em {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...')
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip_address, settings.EMAIL_PORT))
            sock.close()
            connect_time = time.time() - start_time
            
            if result == 0:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Porta {settings.EMAIL_PORT} acessível ({connect_time:.2f}s)'))
            else:
                self.stdout.write(self.style.ERROR(f'  ✗ Porta {settings.EMAIL_PORT} inacessível'))
                
        except socket.gaierror:
            self.stdout.write(self.style.ERROR(f'  ✗ Erro DNS: Não foi possível resolver {settings.EMAIL_HOST}'))
        except socket.timeout:
            self.stdout.write(self.style.ERROR(f'  ✗ Timeout ao conectar em {settings.EMAIL_HOST}:{settings.EMAIL_PORT}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Erro de conexão: {str(e)}'))
    
    def test_smtp_authentication(self, timeout):
        """Testa autenticação SMTP"""
        self.stdout.write('\n3. TESTANDO AUTENTICAÇÃO SMTP:')
        
        try:
            # Configurar SSL/TLS conforme settings
            if settings.EMAIL_USE_SSL:
                self.stdout.write('  Conectando via SSL...')
                server = smtplib.SMTP_SSL(
                    host=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    timeout=timeout
                )
            else:
                self.stdout.write('  Conectando via TCP...')
                server = smtplib.SMTP(
                    host=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    timeout=timeout
                )
                server.ehlo()
                
                if settings.EMAIL_USE_TLS:
                    self.stdout.write('  Iniciando TLS...')
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
            
            # Testar login
            self.stdout.write(f'  Autenticando como {settings.EMAIL_HOST_USER}...')
            start_time = time.time()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            auth_time = time.time() - start_time
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ Autenticação bem-sucedida ({auth_time:.2f}s)'))
            
            # Verificar recursos do servidor
            self.stdout.write('  Recursos do servidor:')
            if hasattr(server, 'esmtp_features'):
                for key, value in server.esmtp_features.items():
                    self.stdout.write(f'    {key}: {value}')
            
            server.quit()
            
        except smtplib.SMTPAuthenticationError:
            self.stdout.write(self.style.ERROR('  ✗ Falha na autenticação. Verifique usuário/senha.'))
        except smtplib.SMTPException as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Erro SMTP: {str(e)}'))
        except socket.timeout:
            self.stdout.write(self.style.ERROR(f'  ✗ Timeout durante autenticação SMTP'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Erro inesperado: {str(e)}'))
    
    def test_email_send(self, timeout):
        """Testa envio real de email"""
        self.stdout.write('\n4. TESTANDO ENVIO DE EMAIL:')
        
        test_email = settings.EMAIL_HOST_USER  # Enviar para si mesmo
        test_subject = f'Teste de Email Django - {time.strftime("%Y-%m-%d %H:%M:%S")}'
        test_message = 'Esta é uma mensagem de teste do sistema Django.'
        
        try:
            # Configurar conexão com timeout personalizado
            connection = get_connection(
                backend=settings.EMAIL_BACKEND,
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS,
                use_ssl=settings.EMAIL_USE_SSL,
                timeout=timeout
            )
            
            self.stdout.write(f'  Enviando email para {test_email}...')
            start_time = time.time()
            
            send_mail(
                subject=test_subject,
                message=test_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_email],
                connection=connection,
                fail_silently=False
            )
            
            send_time = time.time() - start_time
            self.stdout.write(self.style.SUCCESS(f'  ✓ Email enviado com sucesso ({send_time:.2f}s)'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Erro ao enviar email: {str(e)}'))