🚀 DevLab — Sistema de Gestão de Projetos Colaborativos
📌 Descrição do Sistema

O DevLab é um sistema web desenvolvido em Django para gerenciar projetos colaborativos de desenvolvimento de software em instituições de ensino.
Ele permite que coordenadores, professores e estudantes organizem projetos, equipes e participações de forma estruturada e eficiente.

✨ Principais Funcionalidades

✅ Gestão de projetos com status e prazos

✅ Criação e gerenciamento de equipes de desenvolvimento

✅ Sistema de liderança de equipes (1 líder por equipe)

✅ Controle de acesso baseado em perfis:

Coordenador

Professor

Estudante

✅ Sistema de solicitação e aprovação de cadastros

✅ Notificações por e-mail

✅ Recuperação de senha

✅ Dashboards personalizados por tipo de usuário

✅ Interface responsiva e moderna

🛠️ Tecnologias Utilizadas
Backend

🐍 Python 3.8+

🌐 Django 4.2.7

Banco de Dados

🗄️ SQLite3 (desenvolvimento)

Frontend

🧩 HTML5

🎨 CSS3

📐 Bootstrap 5.3.0

Outros

🔐 Autenticação: Django Auth System

📧 Email: SMTP (Gmail, SendGrid, etc.)

📋 Pré-requisitos

Antes de instalar o sistema, certifique-se de ter:

✅ Python 3.8 ou superior

✅ pip (gerenciador de pacotes Python)

✅ Git

✅ Servidor SMTP configurado (opcional)

📦 Instalação
1️⃣ Clonar o Repositório
                
        git clone https://github.com/seu-usuario/devlab-projects.git
        cd devlab-projects

2️⃣ Criar Ambiente Virtual
 # Criar ambiente virtual

    python -m venv venv

Ativar o ambiente virtual:

Windows

    venv\Scripts\activate

Linux / Mac

    source venv/bin/activate

3️⃣ Instalar Dependências

    pip install -r requirements.txt

    Conteúdo do requirements.txt
    Django==4.2.7
    psycopg2-binary==2.9.9
    python-decouple==3.8

🗄️ Configuração do Banco de Dados
1️⃣ Configuração

Por padrão, o sistema usa SQLite3 (não requer instalação adicional).

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'devlab_db',
            'USER': 'seu_usuario',
            'PASSWORD': 'sua_senha',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

2️⃣ Criar as Tabelas
# Criar migrações

    python manage.py makemigrations

# Aplicar migrações

    python manage.py migrate


📌 Tabelas criadas:

Usuario (customizado do AbstractUser)

Projeto

Equipe

ParticipacaoProjeto

SolicitacaoCadastro

3️⃣ (Opcional) Popular Banco com Dados de Teste

      python manage.py populate_db

Isso criará:

✅ 1 Coordenador → coord / coord123

✅ 2 Professores → prof1, prof2 / prof123

✅ 10 Estudantes → joao, maria, etc. / aluno123

✅ 4 Projetos de exemplo

✅ 6 Equipes de exemplo

👤 Criar Usuário Administrador (Coordenador)
Método 1 — Via Comando (Recomendado)
python manage.py createsuperuser


Exemplo:

Username: admin

Email: admin@devlab.com

Password: mínimo 8 caracteres

Método 2 — Definir Tipo de Usuário

⚠️ IMPORTANTE: Após criar o superusuário, defina o tipo como Coordenador.

Via Django Admin

Inicie o servidor:

    python manage.py runserver
    Acesse: http://127.0.0.1:8000/admin/

Edite o usuário admin

No campo Tipo, selecione Coordenador

Clique em Salvar

Via Shell Django

    python manage.py shell

    from meuapp.models import Usuario
    user = Usuario.objects.get(username='admin')
    user.tipo = 'coordenador'
    user.save()
    exit()

📧 Configuração de Email (Opcional)

Edite devlab/settings.py:

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'seu_email@gmail.com'
    EMAIL_HOST_PASSWORD = 'sua_senha_de_app'
    DEFAULT_FROM_EMAIL = 'seu_email@gmail.com'

🔐 Gerar Senha de App no Gmail

Acesse Segurança da Conta Google

Ative verificação em duas etapas

Vá em Senhas de app

Gere uma senha para Mail

Use no EMAIL_HOST_PASSWORD

🧪 Testar Email

    python manage.py test_email

Ou (apenas em DEBUG):

    http://127.0.0.1:8000/test-email/

▶️ Rodar o Servidor

    python manage.py runserver

Servidor disponível em:
👉 http://127.0.0.1:8000/

Porta personalizada

    python manage.py runserver 8080

Acesso na rede

    python manage.py runserver 0.0.0.0:8000

🧪 Testes da Aplicação
🌐 Teste via Navegador

Páginas Públicas

    Home: /
    
    Login: /login/
    
    Registro: /registro/
    
    Dashboards (login necessário)
    
    Dashboard: /dashboard/
    
    Projetos: /projetos/
    
    Equipes: /equipes/

🐍 Teste via Python (requests)
    import requests
    
    BASE_URL = 'http://127.0.0.1:8000'
    
    session = requests.Session()
    login_url = f'{BASE_URL}/login/'
    
    response = session.get(login_url)
    csrf_token = session.cookies['csrftoken']
    
    login_data = {
        'username': 'coord',
        'password': 'coord123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    session.post(login_url, data=login_data)
    
    response = session.get(f'{BASE_URL}/projetos/')
    print(response.status_code)

💻 Teste via cURL

     curl -c cookies.txt -X POST http://127.0.0.1:8000/login/ \
     -d "username=coord&password=coord123"
    
     curl -b cookies.txt http://127.0.0.1:8000/projetos/

📁 Estrutura do Projeto

            devlab-projects/
            ├── devlab/
            │   ├── settings.py
            │   ├── urls.py
            │   └── wsgi.py
            ├── meuapp/
            │   ├── models.py
            │   ├── views.py
            │   ├── forms.py
            │   ├── urls.py
            │   ├── admin.py
            │   └── templates/
            ├── manage.py
            ├── db.sqlite3
            └── requirements.txt

🆘 Solução de Problemas
❌ No module named 'django'

    pip install -r requirements.txt

❌ no such table

    python manage.py migrate

❌ Email não enviado

    python manage.py test_email

🧰 Comandos Úteis

    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py populate_db
    python manage.py test_email
    python manage.py runserver
    python manage.py shell
    python manage.py collectstatic

📄 Licença

Projeto desenvolvido para fins educacionais — DevLab IFB.

👥 Autores

Desenvolvido pela equipe DevLab - Instituto Federal de Brasília    
