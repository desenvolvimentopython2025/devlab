# 📡 Documentação da API - DevLab Projects

## Visão Geral

Esta documentação descreve todos os endpoints disponíveis no sistema DevLab Projects, incluindo métodos HTTP, URLs, parâmetros e exemplos de request/response.

**Base URL**: `http://127.0.0.1:8000`

---

## 🔐 Autenticação

O sistema utiliza **autenticação baseada em sessão** do Django. Todas as rotas protegidas requerem login prévio.

### Fazer Login

**Endpoint**: `/login/`  
**Método**: `POST`  
**Autenticação**: Não requerida  
**Descrição**: Autentica um usuário no sistema

**Parâmetros (Form Data)**:
```json
{
  "username": "string (usuário ou email)",
  "password": "string"
}
```

**Exemplo de Request**:
```http
POST /login/ HTTP/1.1
Content-Type: application/x-www-form-urlencoded

username=coord&password=coord123
```

**Response (Sucesso - 302 Redirect)**:
```
Redireciona para: /dashboard/
Set-Cookie: sessionid=...
```

**Response (Erro - 200)**:
```html
Retorna página de login com mensagem de erro:
"Usuário ou senha inválidos."
```

---

### Fazer Logout

**Endpoint**: `/logout/`  
**Método**: `GET`  
**Autenticação**: Requerida  
**Descrição**: Encerra a sessão do usuário

**Exemplo de Request**:
```http
GET /logout/ HTTP/1.1
Cookie: sessionid=...
```

**Response (302 Redirect)**:
```
Redireciona para: /login/
Mensagem: "Logout realizado com sucesso!"
```

---

## 📊 Projetos

### Listar Projetos

**Endpoint**: `/projetos/`  
**Método**: `GET`  
**Autenticação**: Requerida  
**Descrição**: Lista todos os projetos (coordenador vê todos, outros veem projetos em que participam)

**Query Parameters**:
- `q` (opcional): Busca por título, cliente ou descrição

**Exemplo de Request**:
```http
GET /projetos/?q=notebook HTTP/1.1
Cookie: sessionid=...
```

**Response (200 OK)**:
```html
Página HTML com lista de projetos em formato de tabela
```

**Dados retornados (contexto)**:
```python
{
  'projetos': QuerySet[Projeto],  # Lista de projetos
}
```

---

### Detalhes do Projeto

**Endpoint**: `/projetos/<id>/`  
**Método**: `GET`  
**Autenticação**: Requerida  
**Descrição**: Exibe detalhes completos de um projeto

**Path Parameters**:
- `id` (integer): ID do projeto

**Exemplo de Request**:
```http
GET /projetos/1/ HTTP/1.1
Cookie: sessionid=...
```

**Response (200 OK)**:
```html
Página HTML com detalhes do projeto
```

**Dados retornados (contexto)**:
```python
{
  'projeto': Projeto,              # Objeto do projeto
  'detalhes_completos': boolean,   # True se usuário pode ver tudo
  'equipes': QuerySet[Equipe],     # Equipes do projeto
  'participantes': QuerySet[Usuario]  # Participantes
}
```

**Response (404 Not Found)**:
```html
Página de erro 404
```

---

### Criar Projeto

**Endpoint**: `/projetos/novo/`  
**Método**: `POST`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Cria um novo projeto

**Parâmetros (Form Data)**:
```json
{
  "titulo": "string (max 200)",
  "descricao": "text",
  "cliente": "string (max 200)",
  "status": "planejado|andamento|concluido",
  "data_inicio": "YYYY-MM-DD",
  "data_fim_prevista": "YYYY-MM-DD"
}
```

**Exemplo de Request**:
```http
POST /projetos/novo/ HTTP/1.1
Cookie: sessionid=...
Content-Type: application/x-www-form-urlencoded

titulo=Sistema+Web&descricao=Sistema+para...&cliente=Coordenacao&status=planejado&data_inicio=2024-01-15&data_fim_prevista=2024-06-30
```

**Response (Sucesso - 302 Redirect)**:
```
Redireciona para: /projetos/{id}/
Mensagem: "Projeto '{titulo}' criado com sucesso!"
```

**Response (Erro - 200)**:
```html
Retorna formulário com erros de validação
```

---

### Editar Projeto

**Endpoint**: `/projetos/<id>/editar/`  
**Método**: `POST`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Edita um projeto existente

**Path Parameters**:
- `id` (integer): ID do projeto

**Parâmetros (Form Data)**: Mesmos da criação

**Exemplo de Request**:
```http
POST /projetos/1/editar/ HTTP/1.1
Cookie: sessionid=...
Content-Type: application/x-www-form-urlencoded

titulo=Sistema+Web+V2&status=andamento&...
```

**Response (Sucesso - 302 Redirect)**:
```
Redireciona para: /projetos/{id}/
Mensagem: "Projeto '{titulo}' atualizado com sucesso!"
```

---

### Deletar Projeto

**Endpoint**: `/projetos/<id>/deletar/`  
**Método**: `POST`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Remove um projeto do sistema

**Path Parameters**:
- `id` (integer): ID do projeto

**Exemplo de Request**:
```http
POST /projetos/1/deletar/ HTTP/1.1
Cookie: sessionid=...
```

**Response (Sucesso - 302 Redirect)**:
```
Redireciona para: /projetos/
Mensagem: "Projeto '{titulo}' deletado com sucesso!"
```

---

## 👥 Equipes

### Listar Equipes

**Endpoint**: `/equipes/`  
**Método**: `GET`  
**Autenticação**: Requerida  
**Descrição**: Lista todas as equipes

**Query Parameters**:
- `q` (opcional): Busca por nome da equipe ou projeto

**Exemplo de Request**:
```http
GET /equipes/?q=backend HTTP/1.1
Cookie: sessionid=...
```

**Response (200 OK)**:
```html
Página HTML com lista de equipes
```

---

### Detalhes da Equipe

**Endpoint**: `/equipes/<id>/`  
**Método**: `GET`  
**Autenticação**: Requerida  
**Descrição**: Exibe detalhes de uma equipe

**Path Parameters**:
- `id` (integer): ID da equipe

**Exemplo de Request**:
```http
GET /equipes/1/ HTTP/1.1
Cookie: sessionid=...
```

**Response (200 OK)**:
```python
{
  'equipe': Equipe,
  'detalhes_completos': boolean,
  'membros': QuerySet[Usuario]
}
```

---

### Criar Equipe

**Endpoint**: `/equipes/nova/`  
**Método**: `POST`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Cria uma nova equipe

**Parâmetros (Form Data)**:
```json
{
  "nome": "string (max 100)",
  "descricao": "text (opcional)",
  "projeto": "integer (ID do projeto, opcional)",
  "lider": "integer (ID do usuário, opcional)",
  "membros": "array[integer] (IDs dos usuários)"
}
```

**Exemplo de Request**:
```http
POST /equipes/nova/ HTTP/1.1
Cookie: sessionid=...
Content-Type: application/x-www-form-urlencoded

nome=Equipe+Backend&descricao=API+e+logica&projeto=1&lider=5&membros=5&membros=6
```

**Response (Sucesso - 302 Redirect)**:
```
Redireciona para: /equipes/{id}/
Mensagem: "Equipe '{nome}' criada com sucesso!"
```

---

### Editar Equipe

**Endpoint**: `/equipes/<id>/editar/`  
**Método**: `POST`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Edita uma equipe existente

**Path Parameters**:
- `id` (integer): ID da equipe

**Parâmetros (Form Data)**: Mesmos da criação

**Response (Sucesso - 302 Redirect)**:
```
Redireciona para: /equipes/{id}/
Mensagem: "Equipe '{nome}' atualizada com sucesso!"
```

---

### Deletar Equipe

**Endpoint**: `/equipes/<id>/deletar/`  
**Método**: `POST`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Remove uma equipe

**Path Parameters**:
- `id` (integer): ID da equipe

**Response (Sucesso - 302 Redirect)**:
```
Redireciona para: /equipes/
Mensagem: "Equipe '{nome}' deletada com sucesso!"
```

---

## 👤 Usuários

### Listar Usuários

**Endpoint**: `/usuarios/`  
**Método**: `GET`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Lista todos os usuários do sistema

**Query Parameters**:
- `tipo` (opcional): Filtro por tipo (coordenador, professor, estudante)
- `q` (opcional): Busca por nome, email ou matrícula

**Exemplo de Request**:
```http
GET /usuarios/?tipo=estudante&q=joao HTTP/1.1
Cookie: sessionid=...
```

**Response (200 OK)**:
```html
Página HTML com lista de usuários em tabela
```

---

### Detalhes do Usuário

**Endpoint**: `/usuarios/<id>/`  
**Método**: `GET`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Exibe detalhes de um usuário

**Path Parameters**:
- `id` (integer): ID do usuário

**Response (200 OK)**:
```python
{
  'usuario': Usuario,
  'projetos_participando': QuerySet[Projeto],
  'equipes_participando': QuerySet[Equipe]
}
```

---

### Criar Usuário

**Endpoint**: `/usuarios/novo/`  
**Método**: `POST`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Cria um novo usuário

**Parâmetros (Form Data)**:
```json
{
  "username": "string (max 150, único)",
  "first_name": "string (max 150)",
  "last_name": "string (max 150)",
  "email": "email (único)",
  "tipo": "coordenador|professor|estudante",
  "matricula": "string (max 20, único, opcional)",
  "cpf": "string (11 dígitos, único, opcional)",
  "data_nascimento": "YYYY-MM-DD (opcional)",
  "funcao": "string (max 100, opcional)",
  "password1": "string (mínimo 8 caracteres)",
  "password2": "string (confirmação)"
}
```

**Exemplo de Request**:
```http
POST /usuarios/novo/ HTTP/1.1
Cookie: sessionid=...
Content-Type: application/x-www-form-urlencoded

username=novousuario&first_name=João&last_name=Silva&email=joao@email.com&tipo=estudante&password1=senha123&password2=senha123
```

**Response (Sucesso - 302 Redirect)**:
```
Redireciona para: /usuarios/
Mensagem: "Usuário '{username}' criado com sucesso!"
```

---

### Editar Usuário

**Endpoint**: `/usuarios/<id>/editar/`  
**Método**: `POST`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Edita um usuário existente

**Path Parameters**:
- `id` (integer): ID do usuário

**Parâmetros (Form Data)**: Mesmos da criação, exceto senhas

**Response (Sucesso - 302 Redirect)**:
```
Redireciona para: /usuarios/
Mensagem: "Usuário '{username}' atualizado com sucesso!"
```

---

### Deletar Usuário

**Endpoint**: `/usuarios/<id>/deletar/`  
**Método**: `POST`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Remove um usuário

**Path Parameters**:
- `id` (integer): ID do usuário

**Response (Sucesso - 302 Redirect)**:
```
Redireciona para: /usuarios/
Mensagem: "Usuário '{username}' deletado com sucesso!"
```

---

## 📝 Solicitações de Cadastro

### Solicitar Cadastro (Público)

**Endpoint**: `/registro/`  
**Método**: `POST`  
**Autenticação**: Não requerida  
**Descrição**: Permite que visitantes solicitem cadastro

**Parâmetros (Form Data)**:
```json
{
  "nome_completo": "string (max 150)",
  "email": "email (único)",
  "data_nascimento": "YYYY-MM-DD",
  "password1": "string (mínimo 8 caracteres)",
  "password2": "string (confirmação)"
}
```

**Exemplo de Request**:
```http
POST /registro/ HTTP/1.1
Content-Type: application/x-www-form-urlencoded

nome_completo=Maria+Santos&email=maria@email.com&data_nascimento=2000-05-15&password1=senha123&password2=senha123
```

**Response (Sucesso - 302 Redirect)**:
```
Redireciona para: /login/
Mensagem: "Solicitação de cadastro enviada com sucesso! Você será contatado após análise."
```

---

### Listar Solicitações

**Endpoint**: `/solicitacoes-cadastro/`  
**Método**: `GET`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Lista solicitações de cadastro

**Query Parameters**:
- `status` (opcional): pendente, aprovada, rejeitada, todas (default: pendente)
- `q` (opcional): Busca por nome ou email

**Exemplo de Request**:
```http
GET /solicitacoes-cadastro/?status=pendente HTTP/1.1
Cookie: sessionid=...
```

**Response (200 OK)**:
```python
{
  'solicitacoes': QuerySet[SolicitacaoCadastro],
  'status_atual': 'pendente',
  'total_pendentes': 5,
  'total_aprovadas': 12,
  'total_rejeitadas': 2
}
```

---

### Aprovar Solicitação (AJAX)

**Endpoint**: `/solicitacoes-cadastro/<id>/aprovar/`  
**Método**: `POST`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Aprova uma solicitação e cria o usuário

**Path Parameters**:
- `id` (integer): ID da solicitação

**Exemplo de Request**:
```http
POST /solicitacoes-cadastro/1/aprovar/ HTTP/1.1
Cookie: sessionid=...
Content-Type: application/json
```

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Usuário mariasilva criado com sucesso!"
}
```

**Response (Erro - 400/500)**:
```json
{
  "success": false,
  "message": "Esta solicitação já foi processada."
}
```

---

### Rejeitar Solicitação (AJAX)

**Endpoint**: `/solicitacoes-cadastro/<id>/rejeitar/`  
**Método**: `POST`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Rejeita uma solicitação

**Path Parameters**:
- `id` (integer): ID da solicitação

**Body (JSON)**:
```json
{
  "motivo": "string (obrigatório)"
}
```

**Exemplo de Request**:
```http
POST /solicitacoes-cadastro/1/rejeitar/ HTTP/1.1
Cookie: sessionid=...
Content-Type: application/json

{
  "motivo": "Email inválido"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Solicitação rejeitada com sucesso!"
}
```

---

## 🏠 Dashboards

### Dashboard Principal

**Endpoint**: `/dashboard/`  
**Método**: `GET`  
**Autenticação**: Requerida  
**Descrição**: Redireciona para o dashboard específico do tipo de usuário

**Response (302 Redirect)**:
- Coordenador → `/coordenador/`
- Professor → `/professor/`
- Estudante → `/estudante/`

---

### Dashboard Coordenador

**Endpoint**: `/coordenador/`  
**Método**: `GET`  
**Autenticação**: Requerida (apenas coordenador)  
**Descrição**: Dashboard com estatísticas completas

**Response (200 OK)**:
```python
{
  'projetos': QuerySet[Projeto],      # Últimos 5 projetos
  'equipes': QuerySet[Equipe],        # Últimas 5 equipes
  'usuarios': QuerySet[Usuario],      # Últimos 10 usuários
  'total_projetos': int,
  'total_equipes': int,
  'total_usuarios': int,
  'projetos_planejados': int,
  'projetos_andamento': int,
  'projetos_concluidos': int
}
```

---

### Dashboard Professor

**Endpoint**: `/professor/`  
**Método**: `GET`  
**Autenticação**: Requerida (apenas professor)  
**Descrição**: Dashboard com projetos e equipes do professor

**Response (200 OK)**:
```python
{
  'meus_projetos': QuerySet[Projeto],
  'minhas_equipes': QuerySet[Equipe],
  'todos_projetos': QuerySet[Projeto]
}
```

---

### Dashboard Estudante

**Endpoint**: `/estudante/`  
**Método**: `GET`  
**Autenticação**: Requerida (apenas estudante)  
**Descrição**: Dashboard do estudante

**Response (200 OK)**:
```python
{
  'meus_projetos': QuerySet[Projeto],
  'minhas_equipes': QuerySet[Equipe],
  'equipe_liderada': Equipe | None,
  'todos_projetos': QuerySet[Projeto]
}
```

---

## 👤 Perfil e Senha

### Ver Perfil

**Endpoint**: `/perfil/`  
**Método**: `GET`  
**Autenticação**: Requerida  
**Descrição**: Exibe perfil do usuário logado

**Response (200 OK)**:
```html
Página com dados do usuário e formulário de alteração de senha
```

---

### Alterar Senha

**Endpoint**: `/perfil/`  
**Método**: `POST`  
**Autenticação**: Requerida  
**Descrição**: Altera a senha do usuário logado

**Parâmetros (Form Data)**:
```json
{
  "old_password": "string",
  "new_password1": "string (mínimo 8 caracteres)",
  "new_password2": "string (confirmação)"
}
```

**Response (Sucesso - 302 Redirect)**:
```
Redireciona para: /perfil/
Mensagem: "Senha alterada com sucesso."
```

---

## 🔒 Recuperação de Senha

### Solicitar Reset

**Endpoint**: `/password-reset/`  
**Método**: `POST`  
**Autenticação**: Não requerida  
**Descrição**: Envia email para reset de senha

**Parâmetros (Form Data)**:
```json
{
  "email": "email"
}
```

**Response (302 Redirect)**:
```
Redireciona para: /password-reset/done/
```

---

## 📑 Códigos de Status HTTP

| Código | Significado |
|--------|-------------|
| 200 | Requisição bem-sucedida |
| 302 | Redirecionamento (sucesso em ações) |
| 400 | Requisição inválida (dados incorretos) |
| 401 | Não autenticado |
| 403 | Não autorizado (sem permissão) |
| 404 | Recurso não encontrado |
| 500 | Erro interno do servidor |

---

## 🔐 Permissões por Tipo de Usuário

| Endpoint | Coordenador | Professor | Estudante | Público |
|----------|-------------|-----------|-----------|---------|
| `/login/` | ✅ | ✅ | ✅ | ✅ |
| `/registro/` | ✅ | ✅ | ✅ | ✅ |
| `/projetos/` | ✅ Todos | ✅ Seus | ✅ Seus | ❌ |
| `/projetos/novo/` | ✅ | ❌ | ❌ | ❌ |
| `/equipes/` | ✅ Todas | ✅ Suas | ✅ Suas | ❌ |
| `/equipes/nova/` | ✅ | ❌ | ❌ | ❌ |
| `/usuarios/` | ✅ | ❌ | ❌ | ❌ |
| `/solicitacoes-cadastro/` | ✅ | ❌ | ❌ | ❌ |

---

**Versão da API**: 1.0.0  
**Última Atualização**: Dezembro 2024
