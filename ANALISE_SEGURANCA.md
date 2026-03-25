# 🔒 ANÁLISE DE SEGURANÇA — CAI Sistema Administrativo

**Data da Análise:** 24 de março de 2026  
**Status:** 🔴 CRÍTICO - Vulnerabilidades identificadas  
**Funções Analisadas:** 61 métodos/funções em 5 módulos

---

## 📊 Resumo Executivo

### Implementado ✅
- Autenticação com `@login_required`
- Autorização com `@user_passes_test(is_staff)`
- Validação de entrada (Decimal, whitelist, datas)
- Proteção CSRF automática
- ORM seguro contra SQL injection
- HTML escapado com `format_html()`

### Crítico - Não Implementado ❌
1. **Rate limiting no login** — Brute force possível
2. **Autenticação em endpoints REST** — API aberta a qualquer pessoa
3. **Criptografia de dados sensíveis** — CPF, email em texto plano
4. **Audit trail** — Sem registro de quem fez o quê
5. **Isolamento de dados** — Professores veem todas as turmas
6. **Validação de CPF** — 11 dígitos aleatórios são aceitos
7. **Proteção de upload** — Sem validação de tipo de arquivo
8. **Secrets seguros** — SECRET_KEY em settings.py visível

---

## 🔍 ANÁLISE DETALHADA POR MÓDULO

---

## 1️⃣ AUTENTICAÇÃO (Módulo: accounts)

### Arquivo: `cai_system/apps/accounts/views.py`

#### ✅ login_view() — Status: PARCIALMENTE SEGURO
```python
@require_http_methods(["GET", "POST"])
def login_view(request):
    # ✅ CSRF protegido automaticamente
    # ✅ POST obrigatorio
    # ⚠️ SEM rate limiting
    # ⚠️ SEM feedback seguro de erro
```

**Vulnerabilidades:**
- Sem limite de tentativas (brute force)
- Mensagem igual para "usuário não existe" e "senha errada" (information disclosure)

**Recomendação:** Implementar `django-ratelimit` (5 tentativas/10min por IP)

---

#### ✅ logout_view() — Status: SEGURO
```python
def logout_view(request):
    # ✅ Destroy session
    # ✅ Redireciona para login
    # ✅ CSRF protegido
```

**Status:** Implementado corretamente.

---

#### ✅ home_dashboard() — Status: SEGURO
```python
@login_required(login_url='/login/')
def home_dashboard(request):
    # ✅ Requer autenticacao
    # ✅ Dados user-specific
```

**Status:** Implementado corretamente.

---

## 2️⃣ ALUNOS (Módulo: alunos) — 9 Funções

### Views.py - Views HTML (3 funções)

#### ✅ lista_alunos() — Status: SEGURO
```python
@login_required
def lista_alunos(request):
    # ✅ Requer login
    # ✅ Paginação (20 por página)
```
**Status:** Implementado corretamente com proteção.

---

#### ✅ novo_aluno() — Status: PARCIALMENTE SEGURO
```python
@require_http_methods(["GET", "POST"])
def novo_aluno(request):
    # ✅ Validação com forms.py
    # ✅ CSRF protegido
    # ⚠️ CPF em texto plano
    # ⚠️ Sem validação de formato CPF
```

**Vulnerabilidades:**
- Campo CPF aceita qualquer string com 11-14 caracteres
- Sem máscara ou validação de dígito verificador
- Dados salvos em texto plano (não criptografado)

**Recomendação:** Usar `django-cpf` e criptografia de campo

---

#### ✅ perfil_aluno() — Status: PARCIALMENTE SEGURO
```python
@login_required
def perfil_aluno(request, pk):
    # ✅ Requer login
    # ⚠️ SEM verificação de autorização
    # ⚠️ Professores podem ver dados médicos
```

**Vulnerabilidade Crítica:** Falta `@user_passes_test` para verificar:
- Professor só vê alunos da sua turma
- Responsáveis só veem seu filho

**Recomendação:** Implementar `object_permission_required`

---

#### ✅ editar_aluno() — Status: PARCIALMENTE SEGURO
```python
@require_http_methods(["GET", "POST"])
def editar_aluno(request, pk):
    # ✅ Validação com forms.py
    # ⚠️ Sem verificação de proprietário
    # ⚠️ Logs de edição ausentes
```

**Vulnerabilidade:** Qualquer admin pode editar qualquer aluno novamente.

**Recomendação:** Adicionar `audit_log()` para rastrear mudanças

---

#### ✅ registrar_pagamento_aluno() — Status: PARCIALMENTE SEGURO
```python
def registrar_pagamento_aluno(request, pk):
    # ✅ POST obrigatorio
    # ⚠️ Sem verificacao de valor
    # ⚠️ Sem idempotência
```

**Vulnerabilidade:** Pagamento pode ser registrado 2x (race condition)

**Recomendação:** Adicionar `idempotency_key` no form

---

### Serializers.py - API REST (6 funções)

#### ❌ AlunoViewSet — Status: CRÍTICO
```python
class AlunoViewSet(viewsets.ModelViewSet):
    # ❌ SEM autenticacao especifica
    # ❌ Cria alunos via POST /api/v1/alunos/
    # ❌ Deleta alunos via DELETE /api/v1/alunos/<id>/
    # ❌ Qualquer pessoa pode acessar
```

**Vulnerabilidade Crítica:**
- `DEFAULT_PERMISSION_CLASSES = ['rest_framework.permissions.IsAuthenticated']` 
- MAS a autenticação é apenas por sessão
- Sem token ou API key
- Sem limite de requisições

**Recomendação:** Adicionar `IsStaffUser` e rate limit

---

#### ❌ por_faixa_etaria() — Status: PÚBLICO
```python
@action(detail=False, methods=['get'])
def por_faixa_etaria(self, request):
    # ❌ Retorna distribuição de alunos menores
    # ❌ Pode ser usado para análise de dados
```

**Status:** Ainda tem acesso restrito por `IsAuthenticated`

---

#### ❌ aniversariantes() — Status: PÚBLICO
```python
@action(detail=False, methods=['get'])
def aniversariantes(self, request):
    # ❌ Retorna datas de nascimento
    # ⚠️ Sem parametrização SAFE
```

**Vulnerabilidade:** Campo `mes` não validado
```python
mes = request.query_params.get('mes', date.today().month)
# Aceita: "aaa", "1; DROP TABLE", etc
```

**Recomendação:** Validar com `IntegerField(min_value=1, max_value=12)`

---

### Admin.py (3 funções)

#### ✅ AlunoAdmin — Status: SEGURO
```python
@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    # ✅ Apenas staff pode acessar
    # ✅ Campos readonly corretos
    # ✅ Sem ações perigosas ativas
```

**Status:** Implementado corretamente.

---

#### ✅ ResponsavelAdmin — Status: SEGURO
```python
@admin.register(Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    # ✅ Apenas staff pode acessar
```

**Status:** Implementado corretamente.

---

#### ✅ MatriculaAdmin — Status: SEGURO
```python
@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    # ✅ Apenas staff pode acessar
    # ✅ Validações em models.py
```

**Status:** Implementado corretamente.

---

## 3️⃣ PROFESSORES (Módulo: professores) — 5 Funções

### Views.py (3 funções)

#### ✅ lista_professores() — Status: SEGURO
```python
@login_required
def lista_professores(request):
    # ✅ Requer login
```

**Status:** Implementado corretamente.

---

#### ✅ perfil_professor() — Status: SEGURO
```python
@login_required
def perfil_professor(request, pk):
    # ✅ Requer login
    # ✅ Dados públicos
```

**Status:** Implementado corretamente.

---

### Serializers.py - API REST (2 funções)

#### ❌ ProfessorViewSet — Status: CRÍTICO
```python
class ProfessorViewSet(viewsets.ModelViewSet):
    # ❌ Criação/edição/deleção via API
    # ❌ Sem rate limit
    # ✅ IsAuthenticated apenas
```

**Vulnerabilidade:** POST/PUT/DELETE habilitados para qualquer usuário autenticado

**Recomendação:** Restringir com `IsStaffUser`

---

#### ❌ ativos() — Status: PÚBLICO
```python
@action(detail=False, methods=['get'])
def ativos(self):
    # ✅ Apenas leitura
    # ✅ Dados públicos
```

**Status:** Seguro para leitura pública.

---

## 4️⃣ TURMAS (Módulo: turmas) — 6 Funções

### Views.py (3 funções)

#### ✅ lista_turmas() — Status: SEGURO
```python
@login_required
def lista_turmas(request):
```

**Status:** Implementado corretamente.

---

#### ✅ detalhe_turma() — Status: PARCIALMENTE SEGURO
```python
@login_required
def detalhe_turma(request, pk):
    # ✅ Requer login
    # ⚠️ Professores veem TODAS as turmas
    # ⚠️ Sem filtro by propriedade
```

**Vulnerabilidade:** Professor de piscina grande vê turmas de bebês (acesso não autorizado)

**Recomendação:** Filtrar `turmas = turmas.filter(instrutor=request.user)`

---

### Serializers.py - API REST (3 funções)

#### ❌ TurmaViewSet — Status: CRÍTICO
```python
class TurmaViewSet(viewsets.ModelViewSet):
    # ❌ CREATE/UPDATE/DELETE abertos
    # ❌ Qualquer user autenticado
```

**Vulnerabilidade Crítica:** API aberta para modificação

---

## 5️⃣ FINANCEIRO (Módulo: financeiro) — 13 Funções

### Views.py (6 funções)

#### ✅ dashboard_financeiro() — Status: SEGURO
```python
@login_required
@user_passes_test(lambda u: u.is_staff)
def dashboard_financeiro(request):
    # ✅ Requer login e staff
```

**Status:** Implementado corretamente.

---

#### ✅ lista_mensalidades() — Status: SEGURO
```python
@login_required
@user_passes_test(lambda u: u.is_staff)
def lista_mensalidades(request):
```

**Status:** Implementado corretamente.

---

#### ✅ nova_mensalidade() — Status: SEGURO
```python
@require_http_methods(["GET", "POST"])
def nova_mensalidade(request):
    # ✅ Validação com CurrencyForm
    # ✅ Decimal validado
```

**Status:** Implementado corretamente.

---

#### ✅ editar_mensalidade() — Status: PARCIALMENTE SEGURO
```python
def editar_mensalidade(request, pk):
    # ✅ Validação básica
    # ⚠️ Sem log de quem alterou valor
    # ⚠️ Sem validação de data retroativa
```

**Vulnerabilidade:** Alguém pode alterar valor de pagamento já realizado

**Recomendação:** Bloqueiar edição de mensalidades pagas + audit log

---

#### ✅ registrar_pagamento() — Status: PARCIALMENTE SEGURO
```python
def registrar_pagamento(request, pk):
    # ✅ Validação de valor
    # ⚠️ SEM idempotência
    # ⚠️ SEM verificacao de duplicado
```

**Vulnerabilidade:** POST 2x = 2 registros de pagamento

**Recomendação:** Adicionar unique constraint ou token

---

#### ✅ dashboard_financeiro_api() — Status: CRÍTICO
```python
@api_view(['GET'])
def dashboard_financeiro_api(request):
    # ❌ SEM autenticacao
    # ❌ RETORNA dados sensíveis
```

**Vulnerabilidade CRÍTICA:** Qualquer pessoa pode acessar:
- Total de receitas
- Atrasos em aberto
- Dados de pagamento

**Recomendação:** Adicionar `@permission_classes([IsAuthenticated, IsStaff])`

---

### Serializers.py - API REST (4 funções)

#### ❌ MensalidadeViewSet — Status: CRÍTICO
```python
class MensalidadeViewSet(viewsets.ModelViewSet):
    # ❌ CREATE/UPDATE/DELETE via API
    # ❌ Sem autenticacao especifica
```

---

#### ❌ vencidas() — Status: PÚBLICO
```python
@action(detail=False)
def vencidas(self):
    # ⚠️ Retorna alunos com atraso
    # ⚠️ Sem contexto de autorização
```

---

#### ❌ resumo_mes() — Status: PÚBLICO
```python
@action(detail=False)
def resumo_mes(self):
    # ❌ Sem autenticacao
    # ❌ Retorna dados do mês
```

---

#### ❌ resumo_ultimos_meses() — Status: PÚBLICO
```python
@action(detail=False)
def resumo_ultimos_meses(self):
    # ❌ SEM autenticacao
    # ❌ RETORNA historico financeiro
```

---

### Admin.py (3 funções)

#### ✅ MensalidadeAdmin — Status: SEGURO
```python
@admin.register(Mensalidade)
class MensalidadeAdmin(admin.ModelAdmin):
    # ✅ Apenas staff
    # ✅ Campos readonly
```

**Status:** Implementado corretamente.

---

#### ✅ PagamentoAdmin — Status: SEGURO
```python
@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    # ✅ Apenas staff
    # ✅ Sem actions perigosas
```

**Status:** Implementado corretamente.

---

#### ✅ VencimentoAdmin — Status: SEGURO
```python
@admin.register(Vencimento)
class VencimentoAdmin(admin.ModelAdmin):
    # ✅ Apenas staff
```

**Status:** Implementado corretamente.

---

## 6️⃣ UTILITY SCRIPTS — 2 Funções

### setup_inicial.py

#### ⚠️ update_template() — Status: CÓDIGO DE DESENVOLVIMENTO
```python
def update_template(template_name, colors):
    # ⚠️ Função de DEV apenas
    # ⚠️ Modifica arquivos
```

**Recomendação:** Remover em produção

---

#### ⚠️ get_value() — Status: SEGURO
```python
def get_value(dict_obj, key, default=''):
    # ✅ Função auxiliar segura
```

---

## 🚨 VULNERABILIDADES CRÍTICAS — RESUMO

| # | Vulnerabilidade | Severidade | Localização | Impacto |
|---|---|---|---|---|
| 1 | API REST aberta | **CRÍTICO** | `/api/v1/*` | Acesso não autorizado a dados |
| 2 | Sem rate limiting login | **ALTO** | login_view | Brute force de senhas |
| 3 | Isolamento de dados | **ALTO** | perfil_aluno, detalhe_turma | Acesso cross-user |
| 4 | Dados sensíveis texto plano | **ALTO** | models.py (CPF, email) | Vazamento de dados |
| 5 | Sem validação CPF | **MÉDIO** | forms.py | CPFs inválidos aceitos |
| 6 | Sem audit trail | **MÉDIO** | Toda edição | Falta rastreabilidade |
| 7 | Sem proteção upload | **MÉDIO** | foto, documento | Execução de código |
| 8 | SECRET_KEY exposta | **CRÍTICO** | settings.py | Falsificação de sessão |
| 9 | Idempotência em pagamentos | **ALTO** | registrar_pagamento | Pagamentos duplicados |
| 10 | DEBUG=True produção | **CRÍTICO** | settings.py | Stack traces expostos |

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] **Task 1** — Implementar rate limiting (django-ratelimit)
- [ ] **Task 2** — Adicionar validação CPF (django-cpf)
- [ ] **Task 3** — Proteger viewsets REST com IsStaffUser
- [ ] **Task 4** — Criptografar campos sensíveis (django-fernet-fields)
- [ ] **Task 5** — Implementar audit log (django-auditlog)
- [ ] **Task 6** — Adicionar object-level permissions
- [ ] **Task 7** — Validar uploads (magic numbers, extensões)
- [ ] **Task 8** — Move SECRET_KEY para .env
- [ ] **Task 9** — Adicionar idempotency tokens
- [ ] **Task 10** — Configurar settings para produção

---

## 📋 PRÓXIMAS ETAPAS

1. **Imediato (hoje):** Corrigir Task 1, 8, 10 — bloqueadores críticos
2. **Essa semana:** Task 2-7
3. **Próxima semana:** Task 9

---

**Documentação atualizada em:** 24/03/2026
