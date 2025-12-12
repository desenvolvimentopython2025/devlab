from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from .models import Usuario, Projeto, Equipe, ParticipacaoProjeto
from .forms import (
    UsuarioForm, UsuarioEditForm, ProjetoForm, EquipeForm, 
    ParticipacaoProjetoForm, LoginForm
)


# ============================================================
# FUNÇÕES AUXILIARES PARA VERIFICAÇÃO DE PERMISSÕES
# ============================================================

def is_coordenador(user):
    """Verifica se o usuário é coordenador"""
    return user.is_authenticated and user.tipo == 'coordenador'

def is_professor(user):
    """Verifica se o usuário é professor"""
    return user.is_authenticated and user.tipo == 'professor'

def is_estudante(user):
    """Verifica se o usuário é estudante"""
    return user.is_authenticated and user.tipo == 'estudante'


# ============================================================
# VIEWS DE AUTENTICAÇÃO
# ============================================================

def login_view(request):
    """View para login de usuários"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    """View para logout de usuários"""
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('login')


# ============================================================
# VIEWS DE DASHBOARD
# ============================================================

@login_required
def dashboard(request):
    """Dashboard principal - redireciona baseado no tipo de usuário"""
    user = request.user
    
    if user.tipo == 'coordenador':
        return redirect('coordenador_dashboard')
    elif user.tipo == 'professor':
        return redirect('professor_dashboard')
    else:
        return redirect('estudante_dashboard')


@login_required
@user_passes_test(is_coordenador)
def coordenador_dashboard(request):
    """Dashboard do coordenador com visão completa do sistema"""
    projetos = Projeto.objects.all().order_by('-criado_em')[:5]
    equipes = Equipe.objects.all().order_by('-criada_em')[:5]
    usuarios = Usuario.objects.all().order_by('-date_joined')[:10]
    
    # Estatísticas
    total_projetos = Projeto.objects.count()
    total_equipes = Equipe.objects.count()
    total_usuarios = Usuario.objects.count()
    total_coordenadores = Usuario.objects.filter(tipo='coordenador').count()
    total_professores = Usuario.objects.filter(tipo='professor').count()
    total_estudantes = Usuario.objects.filter(tipo='estudante').count()
    
    # Projetos por status
    projetos_planejados = Projeto.objects.filter(status='planejado').count()
    projetos_andamento = Projeto.objects.filter(status='andamento').count()
    projetos_concluidos = Projeto.objects.filter(status='concluido').count()
    
    context = {
        'projetos': projetos,
        'equipes': equipes,
        'usuarios': usuarios,
        'total_projetos': total_projetos,
        'total_equipes': total_equipes,
        'total_usuarios': total_usuarios,
        'total_coordenadores': total_coordenadores,
        'total_professores': total_professores,
        'total_estudantes': total_estudantes,
        'projetos_planejados': projetos_planejados,
        'projetos_andamento': projetos_andamento,
        'projetos_concluidos': projetos_concluidos,
    }
    return render(request, 'coordenador.html', context)


@login_required
@user_passes_test(is_professor)
def professor_dashboard(request):
    """Dashboard do professor"""
    # Projetos e equipes em que o professor participa
    meus_projetos = request.user.projetos_participando.all()
    minhas_equipes = request.user.equipes_participando.all()
    
    # Todos os projetos (visualização limitada)
    todos_projetos = Projeto.objects.all()
    
    context = {
        'meus_projetos': meus_projetos,
        'minhas_equipes': minhas_equipes,
        'todos_projetos': todos_projetos,
    }
    return render(request, 'professor.html', context)


@login_required
@user_passes_test(is_estudante)
def estudante_dashboard(request):
    """Dashboard do estudante"""
    # Projetos e equipes do estudante
    # Inclui projetos em que o usuário tenha ParticipacaoProjeto OU pertença a uma equipe
    projetos_via_participacao = request.user.projetos_participando.all()
    projetos_via_equipes = Projeto.objects.filter(equipes__membros=request.user)
    meus_projetos = (projetos_via_participacao | projetos_via_equipes).distinct()
    minhas_equipes = request.user.equipes_participando.all()
    equipe_liderada = getattr(request.user, 'equipe_liderada', None)
    
    # Todos os projetos (visualização limitada)
    todos_projetos = Projeto.objects.all()
    
    context = {
        'meus_projetos': meus_projetos,
        'minhas_equipes': minhas_equipes,
        'equipe_liderada': equipe_liderada,
        'todos_projetos': todos_projetos,
    }
    return render(request, 'aluno.html', context)


# ============================================================
# VIEWS DE PROJETOS (CRUD)
# ============================================================

@login_required
def projeto_lista(request):
    """Lista todos os projetos (coordenador) ou projetos do usuário"""
    # Coordenador vê todos; professores e estudantes também poderão ver todos os projetos
    # (detalhes completos continuam restritos em projeto_detalhes)
    projetos = Projeto.objects.all()
    
    # Busca
    query = request.GET.get('q')
    if query:
        projetos = projetos.filter(
            Q(titulo__icontains=query) | 
            Q(cliente__icontains=query) |
            Q(descricao__icontains=query)
        )
    
    return render(request, 'projetos/lista.html', {'projetos': projetos})


@login_required
def projeto_detalhes(request, pk):
    """Detalhes de um projeto"""
    projeto = get_object_or_404(Projeto, pk=pk)
    
    # Verifica se o usuário tem permissão para ver detalhes completos
    if request.user.tipo == 'coordenador' or projeto in request.user.projetos_participando.all():
        detalhes_completos = True
    else:
        detalhes_completos = False
    
    equipes = projeto.equipes.all()
    # participantes agora são todos os membros das equipes associadas ao projeto
    participantes = projeto.membros_por_equipes()
    
    context = {
        'projeto': projeto,
        'detalhes_completos': detalhes_completos,
        'equipes': equipes,
        'participantes': participantes,
    }
    return render(request, 'projetos/detalhes.html', context)


@login_required
@user_passes_test(is_coordenador)
def projeto_criar(request):
    """Criar novo projeto (apenas coordenador)"""
    if request.method == 'POST':
        form = ProjetoForm(request.POST)
        if form.is_valid():
            projeto = form.save()
            messages.success(request, f'Projeto "{projeto.titulo}" criado com sucesso!')
            return redirect('projeto_detalhes', pk=projeto.pk)
    else:
        form = ProjetoForm()
    
    return render(request, 'projetos/form.html', {'form': form, 'acao': 'Criar'})


@login_required
@user_passes_test(is_coordenador)
def projeto_editar(request, pk):
    """Editar projeto existente (apenas coordenador)"""
    projeto = get_object_or_404(Projeto, pk=pk)
    
    if request.method == 'POST':
        form = ProjetoForm(request.POST, instance=projeto)
        if form.is_valid():
            projeto = form.save()
            messages.success(request, f'Projeto "{projeto.titulo}" atualizado com sucesso!')
            return redirect('projeto_detalhes', pk=pk)
    else:
        form = ProjetoForm(instance=projeto)
    
    return render(request, 'projetos/form.html', {
        'form': form, 
        'acao': 'Editar', 
        'projeto': projeto
    })


@login_required
@user_passes_test(is_coordenador)
def projeto_deletar(request, pk):
    """Deletar projeto (apenas coordenador)"""
    projeto = get_object_or_404(Projeto, pk=pk)
    
    if request.method == 'POST':
        titulo = projeto.titulo
        projeto.delete()
        messages.success(request, f'Projeto "{titulo}" deletado com sucesso!')
        return redirect('projeto_lista')
    
    return render(request, 'projetos/confirmar_delete.html', {'projeto': projeto})


# ============================================================
# VIEWS DE EQUIPES (CRUD)
# ============================================================

@login_required
def equipe_lista(request):
    """Lista todas as equipes (coordenador) ou equipes do usuário"""
    # Coordenador vê todas; professores e estudantes também poderão ver todas as equipes
    equipes = Equipe.objects.all()
    
    # Busca
    query = request.GET.get('q')
    if query:
        equipes = equipes.filter(
            Q(nome__icontains=query) | 
            Q(projeto__titulo__icontains=query)
        )
    
    return render(request, 'equipes/lista.html', {'equipes': equipes})


@login_required
def equipe_detalhes(request, pk):
    """Detalhes de uma equipe"""
    equipe = get_object_or_404(Equipe, pk=pk)
    
    # Verifica se o usuário tem permissão para ver detalhes completos
    if request.user.tipo == 'coordenador' or equipe in request.user.equipes_participando.all():
        detalhes_completos = True
    else:
        detalhes_completos = False
    
    membros = equipe.membros.all()
    
    context = {
        'equipe': equipe,
        'detalhes_completos': detalhes_completos,
        'membros': membros,
    }
    return render(request, 'equipes/detalhes.html', context)


@login_required
@user_passes_test(is_coordenador)
def equipe_criar(request):
    """Criar nova equipe (apenas coordenador)"""
    if request.method == 'POST':
        form = EquipeForm(request.POST)
        if form.is_valid():
            equipe = form.save()
            messages.success(request, f'Equipe "{equipe.nome}" criada com sucesso!')
            return redirect('equipe_detalhes', pk=equipe.pk)
    else:
        form = EquipeForm()
    
    return render(request, 'equipes/form.html', {'form': form, 'acao': 'Criar'})


@login_required
@user_passes_test(is_coordenador)
def equipe_editar(request, pk):
    """Editar equipe existente (apenas coordenador)"""
    equipe = get_object_or_404(Equipe, pk=pk)
    
    if request.method == 'POST':
        form = EquipeForm(request.POST, instance=equipe)
        if form.is_valid():
            equipe = form.save()
            messages.success(request, f'Equipe "{equipe.nome}" atualizada com sucesso!')
            return redirect('equipe_detalhes', pk=pk)
    else:
        form = EquipeForm(instance=equipe)
    
    return render(request, 'equipes/form.html', {
        'form': form, 
        'acao': 'Editar', 
        'equipe': equipe
    })


@login_required
@user_passes_test(is_coordenador)
def equipe_deletar(request, pk):
    """Deletar equipe (apenas coordenador)"""
    equipe = get_object_or_404(Equipe, pk=pk)
    
    if request.method == 'POST':
        nome = equipe.nome
        equipe.delete()
        messages.success(request, f'Equipe "{nome}" deletada com sucesso!')
        return redirect('equipe_lista')
    
    return render(request, 'equipes/confirmar_delete.html', {'equipe': equipe})


# ============================================================
# VIEWS DE USUÁRIOS (CRUD - apenas coordenador)
# ============================================================

@login_required
@user_passes_test(is_coordenador)
def usuario_lista(request):
    """Lista todos os usuários (apenas coordenador)"""
    usuarios = Usuario.objects.all().order_by('tipo', 'username')
    
    # Filtro por tipo
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        usuarios = usuarios.filter(tipo=tipo_filtro)
    
    # Busca
    query = request.GET.get('q')
    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(matricula__icontains=query)
        )
    
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})


@login_required
@user_passes_test(is_coordenador)
def usuario_criar(request):
    """Criar novo usuário (apenas coordenador)"""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuário "{usuario.username}" criado com sucesso!')
            return redirect('usuario_lista')
    else:
        form = UsuarioForm()
    
    return render(request, 'usuarios/form.html', {'form': form, 'acao': 'Criar'})


@login_required
@user_passes_test(is_coordenador)
def usuario_editar(request, pk):
    """Editar usuário existente (apenas coordenador)"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuário "{usuario.username}" atualizado com sucesso!')
            return redirect('usuario_lista')
    else:
        form = UsuarioEditForm(instance=usuario)
    
    return render(request, 'usuarios/form.html', {
        'form': form, 
        'acao': 'Editar', 
        'usuario': usuario
    })


@login_required
@user_passes_test(is_coordenador)
def usuario_deletar(request, pk):
    """Deletar usuário (apenas coordenador)"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuário "{username}" deletado com sucesso!')
        return redirect('usuario_lista')
    
    return render(request, 'usuarios/confirmar_delete.html', {'usuario': usuario})


# ============================================================
# VIEW PÚBLICA
# ============================================================

def home(request):
    """Página inicial pública com opção de login e contato da coordenação."""
    coordenacao = {
        'nome': 'Coordenação de Projetos',
        'email': 'coordenacao@example.edu.br',
        'telefone': '+55 (61) 99999-0000',
        'local': 'Bloco A, Sala 101',
        'horario': 'Seg–Sex 09:00–17:00',
    }

    return render(request, 'home.html', {'coordenacao': coordenacao})

def visitante_view(request):
    """View pública para visitantes"""
    projetos = Projeto.objects.all()
    total_projetos = projetos.count()
    total_equipes = Equipe.objects.count()
    
    coordenacao = {
        'nome': 'Coordenação de Projetos',
        'email': 'coordenacao@example.edu.br',
        'telefone': '+55 (61) 99999-0000',
        'local': 'Bloco A, Sala 101',
        'horario': 'Seg–Sex 09:00–17:00',
    }

    context = {
        'projetos': projetos,
        'total_projetos': total_projetos,
        'total_equipes': total_equipes,
        'coordenacao': coordenacao,
    }
    return render(request, 'visitantes.html', context)
# ============================================================
 #Teste botão conta
@login_required
def perfil (request):
    """Exibe o perfil do usuário logado"""
    user = request.user

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        # Verifica senha atual
        if not user.check_password(old_password):
            messages.error(request, 'Senha atual incorreta.')
            return render(request, 'perfil.html', {'user': user})

        # Verifica coincidência das novas senhas
        if new_password1 != new_password2:
            messages.error(request, 'As senhas novas não coincidem.')
            return render(request, 'perfil.html', {'user': user})

        # Validação de força de senha
        try:
            validate_password(new_password1, user)
        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)
            return render(request, 'perfil.html', {'user': user})

        # Tudo ok: altera a senha e atualiza sessão
        user.set_password(new_password1)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Senha alterada com sucesso.')
        return redirect('perfil')

    return render(request, 'perfil.html', {'user': user})



