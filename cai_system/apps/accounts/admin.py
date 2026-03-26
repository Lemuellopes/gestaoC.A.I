from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'perfil', 'ativo', 'is_active')
    list_filter = ('perfil', 'ativo', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('first_name',)

    fieldsets = UserAdmin.fieldsets + (
        ('Dados do C.A.I', {
            'fields': ('perfil', 'telefone', 'foto', 'ativo')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Dados do C.A.I', {
            'fields': ('perfil', 'telefone', 'first_name', 'last_name', 'email')
        }),
    )
