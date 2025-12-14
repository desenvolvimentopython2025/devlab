from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import random
import string

class Usuario(AbstractUser):
    """Modelo de usuário customizado para o sistema DevLab"""
    TIPO_CHOICES = [
        ('coordenador', 'Coordenador'),
        ('professor', 'Professor'),
        ('estudante', 'Estudante'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='estudante')
    matricula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    cpf = models.CharField(max_length=11, unique=True, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    curso = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_tipo_display()})"


class Projeto(models.Model):
    """Modelo para projetos do DevLab"""
    STATUS_CHOICES = [
        ('planejado', 'Planejado'),
        ('andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
    ]
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    cliente = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planejado')
    data_inicio = models.DateField()
    data_fim_prevista = models.DateField()
    participantes = models.ManyToManyField(Usuario, through='ParticipacaoProjeto', related_name='projetos_participando')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'
        ordering = ['-criado_em']
    
    def __str__(self):
        return self.titulo
    
    def total_participantes(self):
        # Return distinct count of users that are members of equipes linked to this projeto
        return self.membros_por_equipes().count()

    def membros_por_equipes(self):
        """Retorna QuerySet de usuários que são membros das equipes deste projeto.

        Isto considera todos os usuários que aparecem em qualquer Equipe cujo
        campo projeto aponta para este Projeto. Usamos distinct() para evitar
        duplicatas quando um usuário estiver em múltiplas equipes do mesmo projeto.
        """
        return Usuario.objects.filter(equipes_participando__projeto=self).distinct()
    
    def total_equipes(self):
        return self.equipes.count()


class ParticipacaoProjeto(models.Model):
    """Tabela de junção N:N entre Usuário e Projeto"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    data_entrada = models.DateField(auto_now_add=True)
    papel = models.CharField(max_length=100, blank=True, help_text="Ex: Desenvolvedor Backend, Tester, etc.")
    
    class Meta:
        verbose_name = 'Participação em Projeto'
        verbose_name_plural = 'Participações em Projetos'
        unique_together = ['usuario', 'projeto']
    
    def __str__(self):
        return f"{self.usuario.username} em {self.projeto.titulo}"


class Equipe(models.Model):
    """Modelo para equipes de desenvolvimento"""
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    # Allow equipes to exist without being tied to a Projeto (optional association)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='equipes', null=True, blank=True)
    lider = models.OneToOneField(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='equipe_liderada',
        help_text="Líder da equipe (cada usuário pode liderar no máximo uma equipe)"
    )
    membros = models.ManyToManyField(Usuario, related_name='equipes_participando', blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Equipe'
        verbose_name_plural = 'Equipes'
        ordering = ['projeto', 'nome']
    
    def __str__(self):
        project_title = self.projeto.titulo if self.projeto else 'Sem Projeto'
        return f"{self.nome} - {project_title}"
    
    def clean(self):
        """Validação para garantir que o líder também seja membro do projeto"""
        # Nota: validação sobre participação do líder foi removida para permitir
        # que um usuário seja definido como líder mesmo que ainda não esteja
        # associado ao projeto. Validações relacionadas a membros continuam
        # sendo aplicadas em nível de formulário quando apropriado.
    
    def total_membros(self):
        return self.membros.count()


class SolicitacaoCadastro(models.Model):
    """Modelo para solicitações de cadastro de novos usuários"""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
    ]
    
    nome_completo = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField()
    senha_hash = models.CharField(max_length=255)  # Hash da senha
    matricula = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    coordenador_aprovador = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='solicitacoes_aprovadas',
        help_text="Coordenador que aprovou/rejeitou a solicitação"
    )
    motivo_rejeicao = models.TextField(blank=True, help_text="Motivo da rejeição (se aplicável)")
    
    class Meta:
        verbose_name = 'Solicitação de Cadastro'
        verbose_name_plural = 'Solicitações de Cadastro'
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"{self.nome_completo} ({self.status})"
    
    @staticmethod
    def gerar_matricula():
        """Gera uma matrícula aleatória única"""
        while True:
            matricula = ''.join(random.choices(string.digits, k=8))
            if not SolicitacaoCadastro.objects.filter(matricula=matricula).exists():
                return matricula