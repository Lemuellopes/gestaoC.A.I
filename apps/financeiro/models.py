from django.db import models
from django.db.models import Sum
from apps.alunos.models import Aluno
from datetime import date


class Mensalidade(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('paga', 'Paga'),
        ('parcial', 'Parcialmente Paga'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
    ]
    MES_CHOICES = [(i, nome) for i, nome in enumerate([
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ], start=1)]

    aluno = models.ForeignKey(
        Aluno, on_delete=models.PROTECT,
        related_name='mensalidades', verbose_name='Aluno'
    )
    mes = models.IntegerField(choices=MES_CHOICES, verbose_name='Mês')
    ano = models.IntegerField(verbose_name='Ano')
    valor_total = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name='Valor Total (R$)'
    )
    valor_pago = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, verbose_name='Valor Pago (R$)'
    )
    data_vencimento = models.DateField(verbose_name='Data de Vencimento')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name='Status'
    )
    desconto = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, verbose_name='Desconto (R$)'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mensalidade'
        verbose_name_plural = 'Mensalidades'
        ordering = ['-ano', '-mes']
        unique_together = ['aluno', 'mes', 'ano']

    def __str__(self):
        return f"{self.aluno.nome} - {self.get_mes_display()}/{self.ano}"

    @property
    def valor_pendente(self):
        return max(0, self.valor_total - self.desconto - self.valor_pago)

    @property
    def dias_atraso(self):
        if self.status in ('paga', 'cancelada'):
            return 0
        hoje = date.today()
        if hoje > self.data_vencimento:
            return (hoje - self.data_vencimento).days
        return 0

    def atualizar_status(self):
        if self.valor_pago >= (self.valor_total - self.desconto):
            self.status = 'paga'
        elif self.valor_pago > 0:
            self.status = 'parcial'
        elif date.today() > self.data_vencimento:
            self.status = 'vencida'
        else:
            self.status = 'pendente'


class Pagamento(models.Model):
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao_debito', 'Cartão de Débito'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('transferencia', 'Transferência Bancária'),
        ('cheque', 'Cheque'),
    ]

    mensalidade = models.ForeignKey(
        Mensalidade, on_delete=models.PROTECT,
        related_name='pagamentos', verbose_name='Mensalidade'
    )
    valor = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Valor Pago (R$)')
    forma_pagamento = models.CharField(
        max_length=30, choices=FORMA_PAGAMENTO_CHOICES,
        default='pix', verbose_name='Forma de Pagamento'
    )
    data_pagamento = models.DateField(default=date.today, verbose_name='Data do Pagamento')
    comprovante = models.FileField(
        upload_to='comprovantes/', null=True, blank=True, verbose_name='Comprovante'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    registrado_por = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL,
        null=True, verbose_name='Registrado por'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-data_pagamento']

    def __str__(self):
        return f"R$ {self.valor} - {self.mensalidade} ({self.data_pagamento})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Atualiza o valor pago na mensalidade
        total_pago = self.mensalidade.pagamentos.aggregate(
            total=Sum('valor')
        )['total'] or 0
        self.mensalidade.valor_pago = total_pago
        self.mensalidade.atualizar_status()
        self.mensalidade.save()
