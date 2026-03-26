from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    PERFIL_CHOICES = [
        ('admin', 'Administrador'),
        ('coordenacao', 'Coordenação'),
        ('financeiro', 'Financeiro'),
        ('professor', 'Professor'),
    ]

    perfil = models.CharField(
        max_length=20,
        choices=PERFIL_CHOICES,
        default='professor',
        verbose_name='Perfil'
    )
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    foto = models.ImageField(
        upload_to='usuarios/', null=True, blank=True, verbose_name='Foto'
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_perfil_display()})"

    @property
    def is_admin(self):
        return self.perfil == 'admin' or self.is_superuser

    @property
    def is_financeiro(self):
        return self.perfil in ('admin', 'financeiro') or self.is_superuser
