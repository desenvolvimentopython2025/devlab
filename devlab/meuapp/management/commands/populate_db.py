import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from meuapp.models import Usuario, Projeto, Equipe

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de teste (usuários, projetos, equipes).'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando o povoamento do banco de dados...'))

        # Inicializa o Faker para o Brasil
        fake = Faker('pt_BR')

        # --------------------------------------------------
        # 1. Limpar dados existentes (exceto superusuários)
        # --------------------------------------------------
        self.stdout.write('Limpando dados antigos...')
        Equipe.objects.all().delete()
        Projeto.objects.all().delete()
        Usuario.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS('Dados antigos limpos.'))

        # --------------------------------------------------
        # 2. Criar Usuários
        # --------------------------------------------------
        self.stdout.write('Criando 100 usuários...')
        
        # Listas para armazenar usuários criados
        professores = []
        estudantes = []
        
        # Criar 1 Coordenador
        coordenador = Usuario.objects.create_user(
            username='coordenador.master',
            password='123',
            first_name='Admin',
            last_name='DevLab',
            email='coordenador@devlab.com',
            tipo='coordenador',
            is_staff=True, # Coordenadores podem acessar o admin
            matricula=fake.unique.random_number(digits=8)
        )

        # Criar 10 Professores
        for _ in range(10):
            profile = fake.profile(fields=['name', 'mail'])
            first_name, last_name = profile['name'].split(' ', 1)
            username = fake.unique.user_name() # Gera um username único

            professor = Usuario.objects.create_user(
                username=username,
                password='123',
                first_name=first_name,
                last_name=last_name,
                email=profile['mail'],
                tipo='professor',
                matricula=fake.unique.random_number(digits=8)
            )
            professores.append(professor)

        # Criar 89 Estudantes
        for _ in range(89):
            profile = fake.profile(fields=['name', 'mail'])
            first_name, last_name = profile['name'].split(' ', 1)
            username = fake.unique.user_name() # Gera um username único
            estudante = Usuario.objects.create_user(
                username=username,
                password='123',
                first_name=first_name,
                last_name=last_name,
                email=profile['mail'],
                tipo='estudante',
                matricula=fake.unique.random_number(digits=8)
            )
            estudantes.append(estudante)

        self.stdout.write(self.style.SUCCESS(f'{Usuario.objects.count()} usuários criados.'))
        
        # --------------------------------------------------
        # 3. Criar Projetos
        # --------------------------------------------------
        self.stdout.write('Criando 6 projetos...')
        projetos_temas = [
            ("Sistema de Gerenciamento de Laboratórios de TI", "SENAI"),
            ("Plataforma de E-learning com Gamificação", "Ministério da Educação"),
            ("Ferramenta de Análise de Segurança de Redes", "Empresa de Cibersegurança"),
            ("Aplicativo Móvel para Agendamento de Salas de Estudo", "Centro Acadêmico"),
            ("Dashboard de Visualização de Dados de Desempenho", "Diretoria Acadêmica"),
            ("Chatbot de Suporte Técnico para Alunos", "Setor de TI da Instituição")
        ]
        
        projetos = []
        for titulo, cliente in projetos_temas:
            projeto = Projeto.objects.create(
                titulo=titulo,
                descricao=fake.paragraph(nb_sentences=5),
                cliente=cliente,
                status=random.choice(['planejado', 'andamento', 'concluido']),
                data_inicio=fake.date_between(start_date='-1y', end_date='today'),
                data_fim_prevista=fake.date_between(start_date='today', end_date='+1y')
            )
            projetos.append(projeto)
        self.stdout.write(self.style.SUCCESS(f'{len(projetos)} projetos criados.'))

        # --------------------------------------------------
        # 4. Criar Equipes e preenchê-las
        # --------------------------------------------------
        self.stdout.write('Criando 15 equipes e adicionando membros...')
        nomes_equipes = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliet", "Kilo", "Lima", "Mike", "November", "Oscar"]
        
        pool_membros = estudantes + professores
        lideres_disponiveis = list(pool_membros)

        for nome in nomes_equipes:
            if not lideres_disponiveis:
                break # Para se não houver mais líderes disponíveis

            # Escolhe um projeto aleatório
            projeto_aleatorio = random.choice(projetos)
            
            # Escolhe um líder aleatório e o remove da lista de disponíveis
            lider = random.choice(lideres_disponiveis)
            lideres_disponiveis.remove(lider)

            equipe = Equipe.objects.create(
                nome=f"Equipe {nome}",
                descricao=f"Responsável pelo desenvolvimento do projeto {projeto_aleatorio.titulo}.",
                projeto=projeto_aleatorio,
                lider=lider
            )

            # Adiciona membros aleatórios
            num_membros = random.randint(3, 8)
            membros_selecionados = random.sample(pool_membros, k=min(num_membros, len(pool_membros)))
            
            # Garante que o líder esteja na lista de membros
            if lider not in membros_selecionados:
                membros_selecionados.append(lider)

            equipe.membros.set(membros_selecionados)

        self.stdout.write(self.style.SUCCESS(f'{Equipe.objects.count()} equipes criadas.'))
        self.stdout.write(self.style.SUCCESS('Povoamento do banco de dados concluído com sucesso!'))