"""
Middleware de segurança do C.A.I
- Rate limiting no login (bloqueio por IP após tentativas falhas)
- Headers HTTP de segurança
- Log de tentativas suspeitas
"""
import logging
import time
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages

logger = logging.getLogger('apps.accounts')


class SecurityHeadersMiddleware:
    """Adiciona headers de segurança HTTP em todas as respostas."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        return response


class LoginRateLimitMiddleware:
    """
    Bloqueia IPs com muitas tentativas de login falhas.
    Configurável via settings.LOGIN_MAX_ATTEMPTS e LOGIN_LOCKOUT_MINUTES.
    """

    MAX_ATTEMPTS = getattr(settings, 'LOGIN_MAX_ATTEMPTS', 5)
    LOCKOUT_MINUTES = getattr(settings, 'LOGIN_LOCKOUT_MINUTES', 15)

    def __init__(self, get_response):
        self.get_response = get_response

    def _get_client_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')

    def _cache_key(self, ip):
        return f'login_attempts_{ip}'

    def __call__(self, request):
        if request.path == settings.LOGIN_URL and request.method == 'POST':
            ip = self._get_client_ip(request)
            key = self._cache_key(ip)
            attempts = cache.get(key, 0)

            if attempts >= self.MAX_ATTEMPTS:
                logger.warning(
                    f'[RATE_LIMIT] IP {ip} bloqueado após {attempts} tentativas de login.'
                )
                return HttpResponseForbidden(
                    f'<html><body style="font-family:sans-serif;text-align:center;padding:60px">'
                    f'<h2>⚠️ Acesso temporariamente bloqueado</h2>'
                    f'<p>Muitas tentativas de login. Aguarde {self.LOCKOUT_MINUTES} minutos.</p>'
                    f'<a href="{settings.LOGIN_URL}">Tentar novamente</a>'
                    f'</body></html>'
                )

        response = self.get_response(request)

        if request.path == settings.LOGIN_URL and request.method == 'POST':
            ip = self._get_client_ip(request)
            key = self._cache_key(ip)
            if response.status_code in (200, 400):
                # Login falhou (se tivesse redirecionado seria 302)
                attempts = cache.get(key, 0) + 1
                ttl = self.LOCKOUT_MINUTES * 60
                cache.set(key, attempts, ttl)
                logger.info(f'[LOGIN_FAIL] IP {ip} — tentativa {attempts}/{self.MAX_ATTEMPTS}')
            elif response.status_code == 302:
                # Login bem-sucedido — limpa o contador
                cache.delete(key)
                logger.info(f'[LOGIN_OK] IP {ip} — autenticação bem-sucedida')

        return response
