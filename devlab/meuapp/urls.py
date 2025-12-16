from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    # ============================================================
    # AUTENTICAÇÃO
    # ============================================================
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    # Password reset (recuperação de senha)
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset_basic.html',
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html',  # Corrigido para o arquivo existente
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # ============================================================
    # DASHBOARDS
    # ============================================================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('coordenador/', views.coordenador_dashboard, name='coordenador_dashboard'),
    path('professor/', views.professor_dashboard, name='professor_dashboard'),
    path('estudante/', views.estudante_dashboard, name='estudante_dashboard'),
    
    # ============================================================
    # VIEW PÚBLICA
    # ============================================================
    path('visitante/', views.visitante_view, name='visitante'),
    
    # ============================================================
    # CRUD PROJETOS
    # ============================================================
    path('projetos/', views.projeto_lista, name='projeto_lista'),
    path('projetos/novo/', views.projeto_criar, name='projeto_criar'),
    path('projetos/<int:pk>/', views.projeto_detalhes, name='projeto_detalhes'),
    path('projetos/<int:pk>/editar/', views.projeto_editar, name='projeto_editar'),
    path('projetos/<int:pk>/deletar/', views.projeto_deletar, name='projeto_deletar'),
    
    # ============================================================
    # CRUD EQUIPES
    # ============================================================
    path('equipes/', views.equipe_lista, name='equipe_lista'),
    path('equipes/nova/', views.equipe_criar, name='equipe_criar'),
    path('equipes/<int:pk>/', views.equipe_detalhes, name='equipe_detalhes'),
    path('equipes/<int:pk>/editar/', views.equipe_editar, name='equipe_editar'),
    path('equipes/<int:pk>/deletar/', views.equipe_deletar, name='equipe_deletar'),
    
    # ============================================================
    # CRUD USUÁRIOS (apenas coordenador)
    # ============================================================
    path('usuarios/', views.usuario_lista, name='usuario_lista'),
    path('usuarios/novo/', views.usuario_criar, name='usuario_criar'),
    path('usuarios/<int:pk>/', views.usuario_detalhes, name='usuario_detalhes'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/<int:pk>/deletar/', views.usuario_deletar, name='usuario_deletar'),
    
    # ============================================================
    # SOLICITAÇÕES DE CADASTRO (apenas coordenador)
    # ============================================================
    path('solicitacoes-cadastro/', views.solicitacoes_cadastro_lista, name='solicitacoes_cadastro_lista'),
    path('solicitacoes-cadastro/<int:pk>/', views.solicitacao_cadastro_detalhes, name='solicitacao_cadastro_detalhes'),
    path('usuarios/<int:pk>/editar-aluno/', views.solicitacao_cadastro_editar_aluno, name='solicitacao_cadastro_editar_aluno'),

    # ============================================================
    #path('conta/', views.conta, name='conta'),
    path('perfil/', views.perfil, name='perfil'),
    # Password change (allow users to change password from profile)
    # Removido o bloco duplicado de password-reset/ para evitar conflitos
    
    #path(aceitar ou rejeitar solicitação de cadastro)
    path('solicitacoes-cadastro/<int:pk>/aprovar/', views.solicitacao_cadastro_aprovar, name='solicitacao_cadastro_aprovar'),
    path('solicitacoes-cadastro/<int:pk>/rejeitar/', views.solicitacao_cadastro_rejeitar, name='solicitacao_cadastro_rejeitar'),
      path('test-email/', views.test_email_view, name='test_email'),    
]