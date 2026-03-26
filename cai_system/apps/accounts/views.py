"""
Views de autenticação e segurança do C.A.I
"""
import logging
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

logger = logging.getLogger('apps.accounts')


def csrf_failure(request, reason=''):
    """View customizada para falha de CSRF."""
    logger.warning(f'[CSRF_FAIL] IP={request.META.get("REMOTE_ADDR")} path={request.path} reason={reason}')
    return render(request, 'errors/403_csrf.html', status=403)


class PerfilRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que exige login + perfil específico.
    Use: perfis_permitidos = ['admin', 'financeiro']
    """
    perfis_permitidos = []
    raise_exception = True

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        if not self.perfis_permitidos:
            return True
        return user.perfil in self.perfis_permitidos

    def handle_no_permission(self):
        logger.warning(
            f'[ACCESS_DENIED] user={self.request.user} '
            f'path={self.request.path} '
            f'perfil={getattr(self.request.user, "perfil", "N/A")}'
        )
        raise PermissionDenied


class AdminRequiredMixin(PerfilRequiredMixin):
    perfis_permitidos = ['admin']


class FinanceiroRequiredMixin(PerfilRequiredMixin):
    perfis_permitidos = ['admin', 'financeiro']


class GestaoRequiredMixin(PerfilRequiredMixin):
    perfis_permitidos = ['admin', 'coordenacao']
