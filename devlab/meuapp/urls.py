from django.urls import path
from . import views

urlpatterns = [
    # ============================================================
    # AUTENTICAÇÃO
    # ============================================================
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
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
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/<int:pk>/deletar/', views.usuario_deletar, name='usuario_deletar'),
]