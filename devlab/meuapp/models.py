from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

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
        return self.participantes.count()
    
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
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='equipes')
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
        return f"{self.nome} - {self.projeto.titulo}"
    
    def clean(self):
        """Validação para garantir que o líder também seja membro do projeto"""
        if self.lider and self.projeto:
            if not ParticipacaoProjeto.objects.filter(usuario=self.lider, projeto=self.projeto).exists():
                raise ValidationError('O líder deve ser um participante do projeto.')
    
    def total_membros(self):
        return self.membros.count()