"""
Formulários do DevLab Projects
Arquivo: meuapp/forms.py
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Usuario, Projeto, Equipe, ParticipacaoProjeto


# ============================================================
# FORMULÁRIO DE LOGIN
# ============================================================

class LoginForm(forms.Form):
    """Formulário de login do sistema"""
    
    username = forms.CharField(
        max_length=150,
        label='Usuário',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu usuário',
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
            'curso',
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
            'curso': 'Curso',
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
            'curso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Análise e Desenvolvimento de Sistemas'
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
            'curso',
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
            'curso': 'Curso',
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
            'curso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Análise e Desenvolvimento de Sistemas'
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
            'membros': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 10
            }),
        }
        
        help_texts = {
            'lider': 'Cada usuário pode ser líder de no máximo uma equipe',
            'membros': 'Segure Ctrl (Windows/Linux) ou Cmd (Mac) para selecionar múltiplos membros',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas estudantes e professores para membros e líder
        usuarios_disponiveis = Usuario.objects.filter(
            tipo__in=['professor', 'estudante']
        ).order_by('tipo', 'first_name', 'last_name')
        
        self.fields['membros'].queryset = usuarios_disponiveis
        
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
        
        # Verificar se o líder participa do projeto
        if lider and projeto:
            participacao_lider = ParticipacaoProjeto.objects.filter(
                usuario=lider, 
                projeto=projeto
            ).exists()
            
            if not participacao_lider:
                raise forms.ValidationError(
                    f'O líder "{lider.get_full_name() or lider.username}" deve ser um '
                    f'participante do projeto "{projeto.titulo}". '
                    f'Adicione-o ao projeto primeiro através do Django Admin ou criando uma ParticipacaoProjeto.'
                )
        
        # Verificar se os membros participam do projeto
        if membros and projeto:
            for membro in membros:
                participacao = ParticipacaoProjeto.objects.filter(
                    usuario=membro,
                    projeto=projeto
                ).exists()
                
                if not participacao:
                    self.add_error('membros', 
                        f'O membro "{membro.get_full_name() or membro.username}" '
                        f'não participa do projeto "{projeto.titulo}". '
                        f'Adicione-o ao projeto primeiro.'
                    )
        
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