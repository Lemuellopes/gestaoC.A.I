from django.contrib import admin
from .models import Professor, HorarioDisponibilidade


class HorarioInline(admin.TabularInline):
    model = HorarioDisponibilidade
    extra = 1


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especialidade', 'status', 'tipo_contrato', 'data_admissao', 'cidade')
    list_filter = ('especialidade', 'status', 'tipo_contrato', 'cidade')
    search_fields = ('nome', 'cpf', 'email', 'registro_cref')
    inlines = [HorarioInline]
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome', 'cpf', 'rg', 'data_nascimento', 'foto')
        }),
        ('Contato', {
            'fields': ('telefone', 'email')
        }),
        ('Endereço', {
            'fields': ('cep', 'logradouro', 'numero', 'bairro', 'cidade', 'estado'),
            'classes': ('collapse',)
        }),
        ('Dados Profissionais', {
            'fields': (
                'especialidade', 'formacao', 'registro_cref',
                'anos_experiencia', 'tipo_contrato', 'salario'
            )
        }),
        ('Status', {
            'fields': ('status', 'data_admissao', 'data_desligamento', 'bio')
        }),
    )
