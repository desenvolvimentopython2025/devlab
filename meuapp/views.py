from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from django.utils import timezone
from django.core.mail import send_mail
from .models import Usuario, Projeto, Equipe, ParticipacaoProjeto, SolicitacaoCadastro
from .forms import (
    UsuarioForm, UsuarioEditForm, ProjetoForm, EquipeForm, 
    ParticipacaoProjetoForm, LoginForm, SolicitacaoCadastroForm, SolicitacaoCadastroAprovarForm
)
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json


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
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = None
            # Tenta autenticar por username
            user = authenticate(request, username=username_or_email, password=password)
            if user is None:
                # Se não achou, tenta autenticar por e-mail
                try:
                    from .models import Usuario
                    usuario_obj = Usuario.objects.get(email__iexact=username_or_email)
                    user = authenticate(request, username=usuario_obj.username, password=password)
                except Usuario.DoesNotExist:
                    user = None
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
    
    # Buscar últimas solicitações aprovadas para mostrar na home
    solicitacoes_aprovadas = SolicitacaoCadastro.objects.filter(status='aprovada').order_by('-data_aprovacao')[:5]

    context = {
        'coordenacao': coordenacao,
        'solicitacoes_aprovadas': solicitacoes_aprovadas,
    }

    return render(request, 'home.html', context)

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
    return render(request, 'visitante.html', context)
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


# ============================================================
# VIEWS DE REGISTRO E APROVAÇÃO DE CADASTRO
# ============================================================

def registro_view(request):
    """View para registro/solicitação de cadastro de novos usuários"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SolicitacaoCadastroForm(request.POST)
        if form.is_valid():
            solicitacao = form.save()
            messages.success(
                request, 
                'Solicitação de cadastro enviada com sucesso! Você será contatado após análise da coordenação.'
            )
            return redirect('login')
    else:
        form = SolicitacaoCadastroForm()
    
    return render(request, 'registro.html', {'form': form})


@login_required
@user_passes_test(is_coordenador)
def solicitacoes_cadastro_lista(request):
    """Lista todas as solicitações de cadastro para o coordenador"""
    # Filtrar por status
    status = request.GET.get('status', 'pendente')
    status = str(status)  # Garante que status_atual será sempre string
    
    if status == 'todas':
        solicitacoes = SolicitacaoCadastro.objects.all()
    else:
        solicitacoes = SolicitacaoCadastro.objects.filter(status=status)
    
    # Busca por nome ou email
    query = request.GET.get('q')
    if query:
        solicitacoes = solicitacoes.filter(
            Q(nome_completo__icontains=query) | 
            Q(email__icontains=query) |
            Q(matricula__icontains=query)
        )
    
    context = {
        'solicitacoes': solicitacoes,
        'status_atual': status,
        'total_pendentes': SolicitacaoCadastro.objects.filter(status='pendente').count(),
        'total_aprovadas': SolicitacaoCadastro.objects.filter(status='aprovada').count(),
        'total_rejeitadas': SolicitacaoCadastro.objects.filter(status='rejeitada').count(),
    }
    return render(request, 'solicitacoes_cadastro/lista.html', context)


@login_required
@user_passes_test(is_coordenador)
def solicitacao_cadastro_detalhes(request, pk):
    """Detalhes de uma solicitação de cadastro"""
    solicitacao = get_object_or_404(SolicitacaoCadastro, pk=pk)
    
    if request.method == 'POST':
        form = SolicitacaoCadastroAprovarForm(request.POST, instance=solicitacao)
        if form.is_valid():
            status_anterior = solicitacao.status
            solicitacao = form.save(commit=False)
            solicitacao.coordenador_aprovador = request.user
            solicitacao.data_aprovacao = timezone.now()
            # Forçar status para aprovada se o botão de aprovação for usado
            if request.POST.get('status') == 'aprovada':
                solicitacao.status = 'aprovada'
            solicitacao.save()
            
            if solicitacao.status == 'aprovada':
                try:
                    nome_partes = solicitacao.nome_completo.strip().split()
                    first_name = nome_partes[0] if len(nome_partes) > 0 else ''
                    last_name = ' '.join(nome_partes[1:]) if len(nome_partes) > 1 else ''
                    username = solicitacao.email.split('@')[0]
                    username_original = username
                    contador = 1
                    while Usuario.objects.filter(username=username).exists():
                        username = f"{username_original}{contador}"
                        contador += 1
                    usuario = Usuario.objects.create_user(
                        username=username,
                        email=solicitacao.email,
                        first_name=first_name,
                        last_name=last_name,
                        password=None
                    )
                    usuario.password = solicitacao.senha_hash
                    usuario.matricula = solicitacao.matricula
                    usuario.data_nascimento = solicitacao.data_nascimento
                    usuario.tipo = 'estudante'
                    usuario.save()
                    # Enviar e-mail de confirmação
                    send_mail(
                        subject='Cadastro aprovado no DevLab',
                        message=f'Seu cadastro foi aprovado!\n\nMatrícula: {usuario.matricula}\nUsuário: {usuario.username}\nAcesse o sistema com seu e-mail e senha cadastrados.',
                        from_email=None,
                        recipient_list=[usuario.email],
                        fail_silently=True
                    )
                    messages.success(
                        request, 
                        f'Solicitação aprovada com sucesso! Usuário {username} criado e e-mail enviado.'
                    )
                except Exception as e:
                    messages.error(
                        request, 
                        f'Solicitação aprovada, mas houve erro ao criar usuário: {str(e)}'
                    )
            else:
                messages.success(request, 'Solicitação rejeitada com sucesso!')
            
            return redirect('solicitacoes_cadastro_lista')
    else:
        form = SolicitacaoCadastroAprovarForm(instance=solicitacao)
    
    context = {
        'solicitacao': solicitacao,
        'form': form,
    }
    return render(request, 'solicitacoes_cadastro/detalhes.html', context)


@login_required
@user_passes_test(is_coordenador)
def solicitacao_cadastro_editar_aluno(request, pk):
    """View para o coordenador editar cadastro de aluno já aprovado"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Apenas coordenador pode editar
    if request.user.tipo != 'coordenador':
        messages.error(request, 'Você não tem permissão para editar este usuário.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Dados de {usuario.get_full_name() or usuario.username} atualizados com sucesso!')
            return redirect('usuario_detalhes', pk=usuario.pk)
    else:
        form = UsuarioEditForm(instance=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
        'acao': 'Editar',
    }
    return render(request, 'usuarios/form.html', context)


@login_required
@user_passes_test(is_coordenador)
def usuario_detalhes(request, pk):
    """Exibe os detalhes de um usuário (apenas para coordenador)"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Buscar projetos e equipes do usuário
    projetos_participando = usuario.projetos_participando.all()
    equipes_participando = usuario.equipes_participando.all()
    
    context = {
        'usuario': usuario,
        'projetos_participando': projetos_participando,
        'equipes_participando': equipes_participando,
    }
    return render(request, 'usuarios/detalhes.html', context)


@login_required
@user_passes_test(is_coordenador)
@require_POST
def solicitacao_cadastro_aprovar(request, pk):
    """Aprovar solicitação via AJAX"""
    try:
        solicitacao = get_object_or_404(SolicitacaoCadastro, pk=pk)
        
        if solicitacao.status != 'pendente':
            return JsonResponse({
                'success': False, 
                'message': 'Esta solicitação já foi processada.'
            })
        
        # Aprovar solicitação
        solicitacao.status = 'aprovada'
        solicitacao.coordenador_aprovador = request.user
        solicitacao.data_aprovacao = timezone.now()
        solicitacao.save()
        
        # Criar usuário
        nome_partes = solicitacao.nome_completo.strip().split()
        first_name = nome_partes[0] if len(nome_partes) > 0 else ''
        last_name = ' '.join(nome_partes[1:]) if len(nome_partes) > 1 else ''
        username = solicitacao.email.split('@')[0]
        username_original = username
        contador = 1
        
        while Usuario.objects.filter(username=username).exists():
            username = f"{username_original}{contador}"
            contador += 1
        
        usuario = Usuario.objects.create_user(
            username=username,
            email=solicitacao.email,
            first_name=first_name,
            last_name=last_name,
            password=None
        )
        usuario.password = solicitacao.senha_hash
        usuario.matricula = solicitacao.matricula
        usuario.data_nascimento = solicitacao.data_nascimento
        usuario.tipo = 'estudante'
        usuario.save()
        
        # Enviar e-mail
        try:
            send_mail(
                subject='Cadastro aprovado no DevLab',
                message=f'Seu cadastro foi aprovado!\n\nMatrícula: {usuario.matricula}\nUsuário: {usuario.username}\nAcesse o sistema com seu e-mail e senha cadastrados.',
                from_email=None,
                recipient_list=[usuario.email],
                fail_silently=True
            )
        except:
            pass
        
        return JsonResponse({
            'success': True,
            'message': f'Usuário {username} criado com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@user_passes_test(is_coordenador)
@require_POST
def solicitacao_cadastro_rejeitar(request, pk):
    """Rejeitar solicitação via AJAX"""
    try:
        solicitacao = get_object_or_404(SolicitacaoCadastro, pk=pk)
        
        if solicitacao.status != 'pendente':
            return JsonResponse({
                'success': False, 
                'message': 'Esta solicitação já foi processada.'
            })
        
        # Obter motivo do body
        data = json.loads(request.body)
        motivo = data.get('motivo', '')
        
        # Rejeitar solicitação
        solicitacao.status = 'rejeitada'
        solicitacao.motivo_rejeicao = motivo
        solicitacao.coordenador_aprovador = request.user
        solicitacao.data_aprovacao = timezone.now()
        solicitacao.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Solicitação rejeitada com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
    

def test_email_view(request):
    """View para testar configurações de email via web (apenas para DEBUG)"""
    if not settings.DEBUG:
        return HttpResponse("Esta view só está disponível em modo DEBUG.", status=403)
    
    if not request.user.is_superuser:
        return HttpResponse("Acesso restrito a superusuários.", status=403)
    
    output = []
    
    def add_output(text, style="info"):
        """Helper para adicionar saída formatada"""
        if style == "success":
            output.append(f'<div style="color: green; margin: 5px 0;">✓ {text}</div>')
        elif style == "error":
            output.append(f'<div style="color: red; margin: 5px 0;">✗ {text}</div>')
        elif style == "warning":
            output.append(f'<div style="color: orange; margin: 5px 0;">⚠ {text}</div>')
        else:
            output.append(f'<div style="margin: 5px 0;">{text}</div>')
    
    # Testar configurações
    add_output('<h2>Teste de Configuração de Email</h2>')
    add_output('<h3>1. Configurações Django:</h3>')
    
    configs = [
        ('EMAIL_BACKEND', settings.EMAIL_BACKEND),
        ('EMAIL_HOST', settings.EMAIL_HOST),
        ('EMAIL_PORT', settings.EMAIL_PORT),
        ('EMAIL_USE_TLS', settings.EMAIL_USE_TLS),
        ('EMAIL_USE_SSL', settings.EMAIL_USE_SSL),
        ('EMAIL_HOST_USER', settings.EMAIL_HOST_USER),
        ('EMAIL_HOST_PASSWORD', '***' if settings.EMAIL_HOST_PASSWORD else 'NÃO CONFIGURADA'),
        ('DEFAULT_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL),
        ('EMAIL_TIMEOUT', getattr(settings, 'EMAIL_TIMEOUT', 'Não definido')),
    ]
    
    for key, value in configs:
        add_output(f'<strong>{key}:</strong> {value}')
    
    # Testar DNS
    add_output('<h3>2. Teste DNS:</h3>')
    try:
        ip = socket.gethostbyname(settings.EMAIL_HOST)
        add_output(f'Resolvido: {settings.EMAIL_HOST} → {ip}', "success")
    except socket.gaierror:
        add_output(f'DNS não resolvido para: {settings.EMAIL_HOST}', "error")
    
    # Testar porta
    add_output('<h3>3. Teste de Porta:</h3>')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex((settings.EMAIL_HOST, settings.EMAIL_PORT))
    if result == 0:
        add_output(f'Porta {settings.EMAIL_PORT} está acessível', "success")
    else:
        add_output(f'Porta {settings.EMAIL_PORT} está fechada/inacessível', "error")
    sock.close()
    
    # Testar SMTP
    add_output('<h3>4. Teste SMTP:</h3>')
    try:
        if settings.EMAIL_USE_SSL:
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
        else:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            if settings.EMAIL_USE_TLS:
                server.starttls(context=ssl.create_default_context())
        
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        add_output('Autenticação SMTP bem-sucedida', "success")
        server.quit()
    except Exception as e:
        add_output(f'Erro SMTP: {str(e)}', "error")
    
    # Testar envio real
    add_output('<h3>5. Teste de Envio:</h3>')
    test_result = ""
    try:
        from django.core.mail import send_mail
        send_mail(
            'Teste de Email Django',
            'Esta é uma mensagem de teste.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER],  # Enviar para si mesmo
            fail_silently=False
        )
        test_result = '<strong style="color: green;">✓ Email enviado com sucesso!</strong>'
    except Exception as e:
        test_result = f'<strong style="color: red;">✗ Erro: {str(e)}</strong>'
    
    # HTML final
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Teste de Email</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .test-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
            h2 {{ color: #333; }}
            h3 {{ color: #555; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Teste de Configuração de Email</h1>
            <div class="test-section">
                {"".join(output)}
            </div>
            <div class="test-section">
                <h3>Resultado do Envio:</h3>
                {test_result}
            </div>
            <div style="margin-top: 20px;">
                <a href="/">← Voltar</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return HttpResponse(html)