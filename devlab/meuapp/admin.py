from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Projeto, Equipe, ParticipacaoProjeto


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'tipo', 'matricula']
    list_filter = ['tipo', 'is_staff', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'matricula']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('tipo', 'matricula', 'cpf', 'data_nascimento', 'curso')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': ('tipo', 'matricula', 'cpf', 'data_nascimento', 'curso')
        }),
    )


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'cliente', 'status', 'data_inicio', 'data_fim_prevista', 'total_participantes']
    list_filter = ['status', 'data_inicio']
    search_fields = ['titulo', 'cliente', 'descricao']
    date_hierarchy = 'data_inicio'


@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'projeto', 'lider', 'total_membros', 'criada_em']
    list_filter = ['projeto']
    search_fields = ['nome', 'descricao']
    filter_horizontal = ['membros']


@admin.register(ParticipacaoProjeto)
class ParticipacaoProjetoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'projeto', 'papel', 'data_entrada']
    list_filter = ['projeto', 'data_entrada']
    search_fields = ['usuario__username', 'projeto__titulo', 'papel']