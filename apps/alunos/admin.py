from django.contrib import admin
from .models import Responsavel, Aluno


class AlunoInline(admin.TabularInline):
    model = Aluno
    fk_name = 'responsavel_principal'
    fields = ('nome', 'matricula', 'status', 'faixa_etaria')
    extra = 0
    show_change_link = True
    readonly_fields = ('matricula',)


@admin.register(Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    list_display = ('nome', 'parentesco', 'telefone', 'email', 'cidade')
    list_filter = ('parentesco', 'cidade', 'estado')
    search_fields = ('nome', 'cpf', 'email', 'telefone')
    inlines = [AlunoInline]
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome', 'cpf', 'rg', 'parentesco')
        }),
        ('Contato', {
            'fields': ('telefone', 'telefone_emergencia', 'email')
        }),
        ('Endereço', {
            'fields': ('cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'matricula', 'faixa_etaria', 'status', 'data_nascimento', 'responsavel_principal')
    list_filter = ('status', 'faixa_etaria', 'autorizacao_foto')
    search_fields = ('nome', 'matricula')
    readonly_fields = ('matricula', 'criado_em', 'atualizado_em')
    fieldsets = (
        ('Identificação', {
            'fields': ('matricula', 'nome', 'data_nascimento', 'faixa_etaria', 'status', 'foto')
        }),
        ('Responsáveis', {
            'fields': ('responsavel_principal', 'responsavel_secundario')
        }),
        ('Informações Médicas', {
            'fields': ('tipo_sanguineo', 'alergias', 'medicamentos', 'condicoes_especiais', 'plano_saude'),
            'classes': ('collapse',)
        }),
        ('Autorizações', {
            'fields': ('autorizacao_foto', 'autorizacao_saida')
        }),
        ('Outros', {
            'fields': ('observacoes', 'data_matricula'),
            'classes': ('collapse',)
        }),
    )
