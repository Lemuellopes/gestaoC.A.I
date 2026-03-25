from django.contrib import admin
from .models import Mensalidade, Pagamento


class PagamentoInline(admin.TabularInline):
    model = Pagamento
    fields = ('valor', 'forma_pagamento', 'data_pagamento', 'comprovante')
    extra = 0
    readonly_fields = ('criado_em',)


@admin.register(Mensalidade)
class MensalidadeAdmin(admin.ModelAdmin):
    list_display = (
        'aluno', 'mes', 'ano', 'valor_total', 'valor_pago',
        'status', 'data_vencimento', 'dias_atraso'
    )
    list_filter = ('status', 'mes', 'ano')
    search_fields = ('aluno__nome', 'aluno__matricula')
    inlines = [PagamentoInline]
    readonly_fields = ('valor_pago', 'criado_em', 'atualizado_em')

    def dias_atraso(self, obj):
        return obj.dias_atraso
    dias_atraso.short_description = 'Dias em Atraso'


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('mensalidade', 'valor', 'forma_pagamento', 'data_pagamento', 'registrado_por')
    list_filter = ('forma_pagamento', 'data_pagamento')
    search_fields = ('mensalidade__aluno__nome',)
    readonly_fields = ('criado_em',)
