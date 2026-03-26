#!/usr/bin/env python
"""
Script de verificação de segurança do C.A.I
Execute: python check_seguranca.py
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cai_system.settings')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
django.setup()

from django.conf import settings

VERDE  = '\033[92m'
AMARELO = '\033[93m'
VERMELHO = '\033[91m'
RESET  = '\033[0m'
NEGRITO = '\033[1m'

checks = []

def ok(msg):   checks.append((True,  msg))
def warn(msg): checks.append((None,  msg))
def fail(msg): checks.append((False, msg))

print(f"\n{NEGRITO}{'═'*54}")
print("  🔐  C.A.I — Verificação de Segurança")
print(f"{'═'*54}{RESET}\n")

# Secret key
if 'insecure' in settings.SECRET_KEY or 'CHANGE' in settings.SECRET_KEY:
    fail("SECRET_KEY está usando valor padrão inseguro")
else:
    ok("SECRET_KEY configurada com valor seguro")

# Debug mode
if settings.DEBUG:
    warn("DEBUG=True — desative em produção (DJANGO_DEBUG=False)")
else:
    ok("DEBUG=False — modo produção ativo")

# Allowed hosts
if '*' in settings.ALLOWED_HOSTS:
    fail("ALLOWED_HOSTS contém '*' — restrinja aos seus domínios")
elif not settings.ALLOWED_HOSTS:
    fail("ALLOWED_HOSTS está vazio")
else:
    ok(f"ALLOWED_HOSTS configurado: {settings.ALLOWED_HOSTS}")

# Session security
if settings.SESSION_COOKIE_HTTPONLY:
    ok("SESSION_COOKIE_HTTPONLY=True")
else:
    fail("SESSION_COOKIE_HTTPONLY deve ser True")

if settings.CSRF_COOKIE_HTTPONLY:
    ok("CSRF_COOKIE_HTTPONLY=True")
else:
    warn("CSRF_COOKIE_HTTPONLY=False — considere ativar")

if settings.SESSION_COOKIE_AGE == 8 * 60 * 60:
    ok(f"SESSION_COOKIE_AGE={settings.SESSION_COOKIE_AGE}s (8 horas)")
else:
    warn(f"SESSION_COOKIE_AGE={settings.SESSION_COOKIE_AGE}s — verifique se é adequado")

# X-Frame-Options
if settings.X_FRAME_OPTIONS == 'DENY':
    ok("X_FRAME_OPTIONS=DENY (proteção contra clickjacking)")
else:
    warn(f"X_FRAME_OPTIONS={settings.X_FRAME_OPTIONS} — recomendado: DENY")

# Auth user model
if settings.AUTH_USER_MODEL == 'accounts.Usuario':
    ok("AUTH_USER_MODEL customizado (accounts.Usuario)")
else:
    warn("AUTH_USER_MODEL padrão do Django — considere customizar")

# Password validators
validators = settings.AUTH_PASSWORD_VALIDATORS
if len(validators) >= 4:
    ok(f"{len(validators)} validadores de senha configurados")
else:
    warn(f"Apenas {len(validators)} validadores de senha — considere adicionar mais")

# Rate limiting
max_attempts = getattr(settings, 'LOGIN_MAX_ATTEMPTS', 0)
lockout = getattr(settings, 'LOGIN_LOCKOUT_MINUTES', 0)
if max_attempts > 0 and lockout > 0:
    ok(f"Rate limiting: {max_attempts} tentativas, bloqueio de {lockout} min")
else:
    fail("Rate limiting de login não configurado")

# Middleware de segurança
required_mw = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'apps.accounts.middleware.SecurityHeadersMiddleware',
    'apps.accounts.middleware.LoginRateLimitMiddleware',
]
for mw in required_mw:
    if mw in settings.MIDDLEWARE:
        ok(f"Middleware ativo: {mw.split('.')[-1]}")
    else:
        fail(f"Middleware ausente: {mw}")

# REST Framework throttling
rf = settings.REST_FRAMEWORK
throttle_classes = rf.get('DEFAULT_THROTTLE_CLASSES', [])
throttle_rates  = rf.get('DEFAULT_THROTTLE_RATES', {})
if throttle_classes and throttle_rates:
    ok(f"API throttling configurado: {throttle_rates}")
else:
    warn("API throttling não configurado — API pode ser abusada")

# Logs de segurança
log_dir = os.path.join(BASE_DIR, 'logs')
if os.path.isdir(log_dir):
    ok("Diretório de logs existe")
else:
    warn("Diretório de logs não encontrado")

# Produção
if not settings.DEBUG:
    if getattr(settings, 'SECURE_SSL_REDIRECT', False):
        ok("SECURE_SSL_REDIRECT=True")
    else:
        warn("SECURE_SSL_REDIRECT=False — ative em produção com HTTPS")
    if getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0:
        ok(f"HSTS configurado: {settings.SECURE_HSTS_SECONDS}s")
    else:
        warn("HSTS não configurado — ative em produção")

# Resultado
print(f"\n{'─'*54}")
total = len(checks)
aprovados = sum(1 for s, _ in checks if s is True)
avisos    = sum(1 for s, _ in checks if s is None)
falhas    = sum(1 for s, _ in checks if s is False)

for status, msg in checks:
    if status is True:
        print(f"  {VERDE}✅{RESET} {msg}")
    elif status is None:
        print(f"  {AMARELO}⚠️ {RESET} {msg}")
    else:
        print(f"  {VERMELHO}❌{RESET} {msg}")

print(f"\n{'─'*54}")
print(f"  Total: {total}  |  {VERDE}Aprovados: {aprovados}{RESET}  |  {AMARELO}Avisos: {avisos}{RESET}  |  {VERMELHO}Falhas: {falhas}{RESET}")
if falhas == 0 and avisos == 0:
    print(f"\n  {VERDE}{NEGRITO}🏆 Sistema totalmente seguro para produção!{RESET}")
elif falhas == 0:
    print(f"\n  {AMARELO}Sistema seguro para desenvolvimento. Corrija os avisos antes de ir para produção.{RESET}")
else:
    print(f"\n  {VERMELHO}⚠️  Corrija as falhas acima antes de usar em produção.{RESET}")
print(f"{'═'*54}\n")
