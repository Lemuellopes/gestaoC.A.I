# 🛡️ RECOMENDAÇÕES DE SEGURANÇA — CAI Sistema Administrativo

**Atualizado em:** 24 de março de 2026  
**Prioridade:** 🔴 CRÍTICA

---

## 📦 Dependências a Instalar

```bash
pip install django-ratelimit==4.1.0
pip install django-auditlog==3.0.6
pip install django-encrypted-model-fields==0.6.5
pip install python-decouple==3.8
pip install django-cors-headers==4.3.1
```

---

## 1️⃣ RATE LIMITING — Implementação

### Problema
Endpoints de login e API vulneráveis a brute force.

### Solução

**Arquivo:** `requirements.txt`
```txt
django-ratelimit==4.1.0
```

**Arquivo:** `cai_system/apps/accounts/views.py`
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/10m', method='POST')
def login_view(request):
    # Máximo 5 tentativas a cada 10 minutos por IP
    ...
```

**Arquivo:** `cai_system/settings.py`
```python
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
```

**Cache em settings.py:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'cai-cache',
    }
}
```

---

## 2️⃣ VALIDAÇÃO DE CPF — Implementação

### Problema
Campo CPF aceita 11 dígitos aleatórios (111.111.111-11).

### Solução

**Arquivo:** `requirements.txt`
```txt
validate-docbr==1.10
```

**Arquivo:** `cai_system/apps/alunos/forms.py` (novo)
```python
from validate_docbr import CPF

def validar_cpf(cpf_string):
    """Valida CPF com dígito verificador"""
    cpf_limpo = cpf_string.replace('.', '').replace('-', '')
    
    if not CPF().is_valid(cpf_limpo):
        raise ValidationError('CPF inválido')
    
    return cpf_string

class ResponsavelForm(forms.ModelForm):
    class Meta:
        model = Responsavel
        fields = ['nome', 'cpf', 'telefone', 'parentesco']
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            validar_cpf(cpf)
        return cpf
```

---

## 3️⃣ PROTEÇÃO DE API REST — Implementação

### Problema
Endpoints `/api/v1/` permitem CREATE/UPDATE/DELETE para qualquer usuário autenticado.

### Solução

**Arquivo:** `cai_system/apps/accounts/permissions.py` (novo)
```python
from rest_framework import permissions

class IsStaffUser(permissions.BasePermission):
    """Apenas usuários staff podem acessar"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsOwnerOrStaff(permissions.BasePermission):
    """Apenas o proprietário ou staff"""
    
    def has_object_permission(self, request, view, obj):
        # Staff sempre tem acesso
        if request.user.is_staff:
            return True
        
        # Responsáveis veem apenas seus filhos
        if hasattr(obj, 'responsavel_principal'):
            return obj.responsavel_principal.usuario == request.user
        
        # Professores veem apenas suas turmas
        if hasattr(obj, 'instrutor'):
            return obj.instrutor == request.user
        
        return False
```

**Arquivo:** `cai_system/settings.py`
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'apps.accounts.permissions.IsStaffUser',  # ← Adicionar
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

**Arquivo:** `cai_system/apps/alunos/serializers.py`
```python
class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsStaffUser,  # ← Apenas staff cria/edita/deleta
    ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'faixa_etaria']
    search_fields = ['nome', 'matricula']
    
    def get_queryset(self):
        """Filtra alunos baseado em role do usuário"""
        user = self.request.user
        
        if user.is_staff:
            return Aluno.objects.all()
        
        # Responsáveis veem apenas seus filhos
        if hasattr(user, 'responsavel'):
            return Aluno.objects.filter(
                models.Q(responsavel_principal=user.responsavel) |
                models.Q(responsavel_secundario=user.responsavel)
            )
        
        # Professores veem alunos de suas turmas
        if hasattr(user, 'professor'):
            return Aluno.objects.filter(
                matricula__turma__instrutor=user.professor
            ).distinct()
        
        return Aluno.objects.none()  # Padrão: nenhum acesso
```

---

## 4️⃣ CRIPTOGRAFIA DE DADOS SENSÍVEIS — Implementação

### Problema
CPF, email, telefone em texto plano no banco de dados.

### Solução

**Arquivo:** `requirements.txt`
```txt
django-encrypted-model-fields==0.6.5
```

**Arquivo:** `cai_system/settings.py`
```python
# Chave de criptografia (mover para .env em produção)
ENCRYPTED_FIELD_KEY = os.environ.get('ENCRYPTED_FIELD_KEY', 'dev-key-change-in-production')
```

**Arquivo:** `cai_system/apps/alunos/models.py`
```python
from encrypted_model_fields.fields import EncryptedCharField, EncryptedEmailField

class Responsavel(models.Model):
    nome = models.CharField(max_length=150)
    cpf = EncryptedCharField(max_length=14)  # Criptografado
    telefone = EncryptedCharField(max_length=20)  # Criptografado
    email = EncryptedEmailField(blank=True)  # Criptografado
    parentesco = models.CharField(max_length=20, choices=PARENTESCO_CHOICES)
```

**Arquivo:** `cai_system/apps/alunos/models.py`
```python
class Aluno(models.Model):
    nome = models.CharField(max_length=150)
    data_nascimento = models.DateField()
    responsavel_principal = models.ForeignKey(Responsavel, ...)
    # email pode ser adicionado criptografado
    email_aluno = EncryptedEmailField(blank=True)
```

---

## 5️⃣ AUDIT LOG (Rastreamento de Ações) — Implementação

### Problema
Sem registro de quem editou o quê e quando.

### Solução

**Arquivo:** `requirements.txt`
```txt
django-auditlog==3.0.6
```

**Arquivo:** `cai_system/settings.py`
```python
INSTALLED_APPS = [
    ...
    'auditlog',
]
```

**Arquivo:** `cai_system/apps/alunos/models.py`
```python
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

class Aluno(models.Model):
    # ... campos existentes ...
    history = AuditlogHistoryField()

class Responsavel(models.Model):
    # ... campos existentes ...
    history = AuditlogHistoryField()

# Registrar modelos
auditlog.register(Aluno, include_all_fields=True)
auditlog.register(Responsavel, include_all_fields=True)
```

**Arquivo:** `cai_system/apps/financeiro/models.py`
```python
from auditlog.registry import auditlog

auditlog.register(Mensalidade, include_all_fields=True)
auditlog.register(Pagamento, include_all_fields=True)
```

**Template:** `templates/auditlog_history.html` (novo)
```html
<div class="card">
  <h5>Histórico de Alterações</h5>
  <table class="table table-sm">
    <tr>
      <th>Data</th>
      <th>Usuário</th>
      <th>Ação</th>
      <th>Detalhes</th>
    </tr>
    {% for log in object.history.all %}
    <tr>
      <td>{{ log.timestamp|date:"d/m/Y H:i" }}</td>
      <td>{{ log.actor }}</td>
      <td>{{ log.get_action_display }}</td>
      <td>{{ log.changes }}</td>
    </tr>
    {% endfor %}
  </table>
</div>
```

---

## 6️⃣ ISOLAMENTO DE DADOS POR USUÁRIO — Implementação

### Problema
Professores veem todas as turmas. Responsáveis veem dados de outros alunos.

### Solução

**Arquivo:** `cai_system/apps/accounts/permissions.py`
```python
class IsProfessorOfTurma(permissions.BasePermission):
    """Professor vê apenas suas turmas"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        if hasattr(obj, 'instrutor'):
            return obj.instrutor == request.user.professor
        
        return False

class IsResponsavelOfAluno(permissions.BasePermission):
    """Responsáveis veem apenas seus filhos"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        if hasattr(request.user, 'responsavel'):
            return obj.responsavel_principal == request.user.responsavel
        
        return False
```

**Arquivo:** `cai_system/apps/turmas/views.py`
```python
@login_required
def detalhe_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    
    # Verificar autorização
    if not request.user.is_staff:
        if hasattr(request.user, 'professor'):
            if turma.instrutor != request.user.professor:
                raise PermissionDenied("Acesso negado")
    
    context = {
        'turma': turma,
        'matriculas': turma.matricula_set.all()
    }
    return render(request, 'turmas/detalhe.html', context)
```

---

## 7️⃣ PROTEÇÃO DE UPLOAD — Implementação

### Problema
Sem validação de tipo de arquivo (pode executar código).

### Solução

**Arquivo:** `cai_system/apps/alunos/forms.py`
```python
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

def validar_foto(arquivo):
    """Valida arquivo de imagem"""
    valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
    file_extension = arquivo.name.split('.')[-1].lower()
    
    if file_extension not in valid_extensions:
        raise ValidationError('Tipos aceitos: JPG, PNG, GIF')
    
    if arquivo.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError('Arquivo muito grande (máximo 5MB)')
    
    # Validar dimensões
    width, height = get_image_dimensions(arquivo)
    if width < 100 or height < 100:
        raise ValidationError('Imagem muito pequena (mínimo 100x100px)')

def validar_documento(arquivo):
    """Valida documento PDF/DOC"""
    valid_extensions = ['pdf', 'doc', 'docx']
    file_extension = arquivo.name.split('.')[-1].lower()
    
    if file_extension not in valid_extensions:
        raise ValidationError('Tipos aceitos: PDF, DOC, DOCX')
    
    if arquivo.size > 10 * 1024 * 1024:  # 10MB
        raise ValidationError('Arquivo muito grande (máximo 10MB)')

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'data_nascimento', 'foto', ...]
    
    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if foto:
            validar_foto(foto)
        return foto
    
    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if documento:
            validar_documento(documento)
        return documento
```

---

## 8️⃣ SECRETS SEGUROS (.env) — Implementação

### Problema
SECRET_KEY e dados sensíveis em `settings.py` visível.

### Solução

**Arquivo:** `requirements.txt`
```txt
python-decouple==3.8
```

**Arquivo:** `.env` (novo - criar na raiz)
```bash
# Django Config
SECRET_KEY=sua-chave-super-secreta-aqui-mude-em-producao
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com.br

# Database
DATABASE_NAME=db.sqlite3
DATABASE_USER=
DATABASE_PASSWORD=

# Email Config
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app

# Encryption
ENCRYPTED_FIELD_KEY=sua-chave-de-criptografia

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://seu-dominio.com.br
```

**Arquivo:** `.gitignore` (atualizar)
```
.env
.env.local
*.pyc
__pycache__/
*.sqlite3
venv/
.vscode/
```

**Arquivo:** `cai_system/settings.py`
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / config('DATABASE_NAME', default='db.sqlite3'),
    }
}

# Email
EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Encryption
ENCRYPTED_FIELD_KEY = config('ENCRYPTED_FIELD_KEY')
```

---

## 9️⃣ IDEMPOTÊNCIA EM PAGAMENTOS — Implementação

### Problema
Registrar pagamento 2x cria 2 registros (race condition).

### Solução

**Arquivo:** `cai_system/apps/financeiro/models.py`
```python
import uuid

class Pagamento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    mensalidade = models.ForeignKey(Mensalidade, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateTimeField(auto_now_add=True)
    metodo = models.CharField(max_length=20, choices=METODO_PAGAMENTO_CHOICES)
    idempotency_key = models.CharField(max_length=100, unique=True)  # ← Novo
    
    class Meta:
        unique_together = [['mensalidade', 'idempotency_key']]
```

**Arquivo:** `cai_system/apps/financeiro/serializers.py`
```python
class PagamentoViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        idempotency_key = request.headers.get('Idempotency-Key')
        
        if not idempotency_key:
            return Response(
                {'error': 'Header Idempotency-Key obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar se já existe
        existing = Pagamento.objects.filter(
            idempotency_key=idempotency_key
        ).first()
        
        if existing:
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Criar novo
        return super().create(request, *args, **kwargs)
```

---

## 🔟 CONFIGURAÇÃO PARA PRODUÇÃO — settings.py

**Arquivo:** `cai_system/settings.py`
```python
import os
from decouple import config

# ⚠️ PRODUÇÃO
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')  # Obrigatório em produção
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "cdn.jsdelivr.net"),
    'style-src': ("'self'", "cdn.jsdelivr.net"),
}

# HTTPS em produção
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# CORS (apenas origens confiáveis)
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')

# Logging para auditoria
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/cai/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Tempo de sessão
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Instalar todas as dependências
- [ ] Criar arquivo `.env` com secrets
- [ ] Implementar rate limiting
- [ ] Validar CPF
- [ ] Proteger viewsets REST
- [ ] Criptografar campos sensíveis
- [ ] Implementar audit log
- [ ] Isolar dados por usuário
- [ ] Validar uploads
- [ ] Testar em staging
- [ ] Deploy em produção

---

**Data de criação:** 24/03/2026  
**Próxima revisão:** 24/04/2026
