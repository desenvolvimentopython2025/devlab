"""
Formulários do DevLab Projects
Arquivo: meuapp/forms.py
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from .models import Usuario, Projeto, Equipe, ParticipacaoProjeto, SolicitacaoCadastro


# ============================================================
# FORMULÁRIO DE LOGIN
# ============================================================

class LoginForm(forms.Form):
    """Formulário de login do sistema"""
    
    username = forms.CharField(
        max_length=150,
        label='Usuário ou E-mail',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu usuário ou e-mail',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        })
    )


# ============================================================
# FORMULÁRIOS DE USUÁRIO
# ============================================================

class UsuarioForm(UserCreationForm):
    """
    Formulário para criar novo usuário
    Extends UserCreationForm para incluir campos de senha
    """
    
    class Meta:
        model = Usuario
        fields = [
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'tipo', 
            'matricula', 
            'cpf', 
            'data_nascimento', 
            'funcao',
            'password1', 
            'password2' 
        ]
        
        labels = {
            'username': 'Nome de usuário',
            'first_name': 'Primeiro nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'tipo': 'Tipo de usuário',
            'matricula': 'Matrícula',
            'cpf': 'CPF',
            'data_nascimento': 'Data de nascimento',
            'funcao': 'Função',
        }
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: joao.silva'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: João'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Silva'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: joao@email.com'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'matricula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 20240001'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apenas números (11 dígitos)',
                'maxlength': '11'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'funcao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Desenvolvedor Backend, Designer UI/UX'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customizar campos de senha
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite uma senha forte'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        })
        
        # Traduzir labels
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].label = 'Confirmação de senha'
        self.fields['password1'].help_text = 'Mínimo 8 caracteres'


class UsuarioEditForm(forms.ModelForm):
    """
    Formulário para editar usuário existente
    Não inclui campos de senha
    """
    
    class Meta:
        model = Usuario
        fields = [
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'tipo', 
            'matricula', 
            'cpf', 
            'data_nascimento', 
            'funcao',
            'is_active'
        ]
        
        labels = {
            'username': 'Nome de usuário',
            'first_name': 'Primeiro nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'tipo': 'Tipo de usuário',
            'matricula': 'Matrícula',
            'cpf': 'CPF',
            'data_nascimento': 'Data de nascimento',
            'funcao': 'Função',
            'is_active': 'Usuário ativo',
        }
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: joao.silva'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: João'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Silva'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: joao@email.com'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'matricula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 20240001'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apenas números',
                'maxlength': '11'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'funcao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Desenvolvedor Backend, Designer UI/UX'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


# ============================================================
# FORMULÁRIO DE PROJETO
# ============================================================

class ProjetoForm(forms.ModelForm):
    """Formulário para criar e editar projetos"""
    
    class Meta:
        model = Projeto
        fields = [
            'titulo', 
            'descricao', 
            'cliente', 
            'status', 
            'data_inicio', 
            'data_fim_prevista'
        ]
        
        labels = {
            'titulo': 'Título do projeto',
            'descricao': 'Descrição',
            'cliente': 'Cliente',
            'status': 'Status',
            'data_inicio': 'Data de início',
            'data_fim_prevista': 'Data de fim prevista',
        }
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Sistema de Empréstimo de Notebooks'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Descreva os objetivos, escopo e funcionalidades do projeto'
            }),
            'cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Coordenação de Laboratórios'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_fim_prevista': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        
        help_texts = {
            'descricao': 'Descreva o projeto de forma clara e completa',
            'status': 'Planejado: ainda não iniciado | Em andamento: em desenvolvimento | Concluído: finalizado',
        }
    
    def clean(self):
        """Validação customizada para datas"""
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim_prevista = cleaned_data.get('data_fim_prevista')
        
        if data_inicio and data_fim_prevista:
            if data_fim_prevista < data_inicio:
                raise forms.ValidationError(
                    'A data de fim prevista não pode ser anterior à data de início.'
                )
        
        return cleaned_data


# ============================================================
# FORMULÁRIO DE EQUIPE
# ============================================================

class EquipeForm(forms.ModelForm):
    """Formulário para criar e editar equipes"""
    
    class Meta:
        model = Equipe
        fields = ['nome', 'descricao', 'projeto', 'lider', 'membros']
        
        labels = {
            'nome': 'Nome da equipe',
            'descricao': 'Descrição',
            'projeto': 'Projeto',
            'lider': 'Líder da equipe',
            'membros': 'Membros da equipe',
        }
        
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Equipe Backend'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descreva as responsabilidades e objetivos da equipe'
            }),
            'projeto': forms.Select(attrs={
                'class': 'form-control'
            }),
            'lider': forms.Select(attrs={
                'class': 'form-control'
            }),
            'membros': forms.CheckboxSelectMultiple(),
        }
        
        help_texts = {
            'lider': 'Cada usuário pode ser líder de no máximo uma equipe',
            'membros': 'Selecione os usuários que farão parte da equipe.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas estudantes e professores para membros e líder
        usuarios_disponiveis = Usuario.objects.filter(
            tipo__in=['professor', 'estudante']
        ).order_by('tipo', 'first_name', 'last_name')
        
        self.fields['membros'].queryset = usuarios_disponiveis
        # Allow creating an equipe without selecting a projeto
        if 'projeto' in self.fields:
            self.fields['projeto'].required = False
        
        # Para o campo líder, mostrar apenas usuários sem equipe ou o líder atual
        if self.instance.pk:
            # Editando: mostrar usuários sem equipe OU o líder atual desta equipe
            lideres_disponiveis = usuarios_disponiveis.filter(
                Q(equipe_liderada__isnull=True) | Q(equipe_liderada=self.instance)
            )
        else:
            # Criando: mostrar apenas usuários sem equipe
            lideres_disponiveis = usuarios_disponiveis.filter(
                equipe_liderada__isnull=True
            )
        
        self.fields['lider'].queryset = lideres_disponiveis
        self.fields['lider'].required = False
    
    def clean(self):
        """Validações customizadas"""
        cleaned_data = super().clean()
        lider = cleaned_data.get('lider')
        projeto = cleaned_data.get('projeto')
        membros = cleaned_data.get('membros')
        
        # Nota: não é mais obrigatório que o líder seja participante do projeto.
        # Mantemos validação dos membros (abaixo) quando um projeto é selecionado.
        
        # Nota: não é mais necessário que os membros já participem do projeto
        # ao serem adicionados à equipe. Se um projeto estiver selecionado,
        # a associação entre usuário e projeto pode ser criada separadamente
        # por meio do fluxo de ParticipacaoProjeto (admin ou formulário).
        
        return cleaned_data


# ============================================================
# FORMULÁRIO DE PARTICIPAÇÃO EM PROJETO
# ============================================================

class ParticipacaoProjetoForm(forms.ModelForm):
    """Formulário para adicionar participantes a projetos"""
    
    class Meta:
        model = ParticipacaoProjeto
        fields = ['usuario', 'projeto', 'papel']
        
        labels = {
            'usuario': 'Usuário',
            'projeto': 'Projeto',
            'papel': 'Papel/Função no projeto',
        }
        
        widgets = {
            'usuario': forms.Select(attrs={
                'class': 'form-control'
            }),
            'projeto': forms.Select(attrs={
                'class': 'form-control'
            }),
            'papel': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Desenvolvedor Backend, Tester, Designer UI/UX, Scrum Master'
            }),
        }
        
        help_texts = {
            'papel': 'Especifique a função/papel do usuário neste projeto',
        }
    
    def clean(self):
        """Validar se já existe participação"""
        cleaned_data = super().clean()
        usuario = cleaned_data.get('usuario')
        projeto = cleaned_data.get('projeto')
        
        if usuario and projeto:
            # Verificar se já existe (exceto se estamos editando)
            existe = ParticipacaoProjeto.objects.filter(
                usuario=usuario,
                projeto=projeto
            )
            
            if self.instance.pk:
                existe = existe.exclude(pk=self.instance.pk)
            
            if existe.exists():
                raise forms.ValidationError(
                    f'{usuario.get_full_name() or usuario.username} já participa '
                    f'do projeto {projeto.titulo}.'
                )
        
        return cleaned_data


# ============================================================
# FORMULÁRIO DE CADASTRO (REGISTRO)
# ============================================================

class SolicitacaoCadastroForm(forms.ModelForm):
    """Formulário para solicitação de cadastro de novos usuários"""
    
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite uma senha forte (mínimo 8 caracteres)'
        }),
        min_length=8,
        required=True
    )
    
    password2 = forms.CharField(
        label='Confirmação de Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme sua senha'
        }),
        required=True
    )
    
    class Meta:
        model = SolicitacaoCadastro
        fields = ['nome_completo', 'email', 'data_nascimento', 'password1', 'password2']
        
        labels = {
            'nome_completo': 'Nome Completo',
            'email': 'E-mail',
            'data_nascimento': 'Data de Nascimento',
        }
        
        widgets = {
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: João da Silva Santos',
                'autofocus': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: joao.silva@email.com'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Gerar matricula automaticamente (não é exibida no formulário)
        if not self.instance.pk:
            self.instance.matricula = SolicitacaoCadastro.gerar_matricula()
    
    def clean(self):
        """Validações customizadas"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        email = cleaned_data.get('email')
        
        # Validar se as senhas correspondem
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('As senhas não correspondem.')
        
        # Validar se o email já está registrado (em usuários existentes ou solicitações)
        if email:
            if Usuario.objects.filter(email=email).exists():
                raise forms.ValidationError('Este e-mail já está cadastrado no sistema.')
            
            if SolicitacaoCadastro.objects.filter(email=email).exclude(status='rejeitada').exists():
                raise forms.ValidationError('Já existe uma solicitação de cadastro com este e-mail.')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Salvar com hash da senha"""
        instance = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        
        if password:
            instance.senha_hash = make_password(password)
        
        # Garantir que a matrícula seja única
        if not instance.matricula:
            instance.matricula = SolicitacaoCadastro.gerar_matricula()
        
        if commit:
            instance.save()
        return instance


class SolicitacaoCadastroAprovarForm(forms.ModelForm):
    """Formulário para aprovar/rejeitar solicitações de cadastro"""
    
    class Meta:
        model = SolicitacaoCadastro
        fields = ['status', 'motivo_rejeicao']
        
        labels = {
            'status': 'Status',
            'motivo_rejeicao': 'Motivo da Rejeição',
        }
        
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'motivo_rejeicao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explique o motivo da rejeição (obrigatório se rejeitado)'
            }),
        }
    
    def clean(self):
        """Validar se motivo é preenchido quando rejeita"""
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        motivo = cleaned_data.get('motivo_rejeicao')
        
        if status == 'rejeitada' and not motivo:
            raise forms.ValidationError('O motivo da rejeição é obrigatório ao rejeitar uma solicitação.')
        
        return cleaned_data