from datetime import date
from calendar import monthrange
from decimal import Decimal

from django.db.models import Q

from .models import Mensalidade
from apps.turmas.models import Matricula


def gerar_cobrancas_do_mes(mes, ano):
    inicio_mes = date(ano, mes, 1)
    fim_mes = date(ano, mes, monthrange(ano, mes)[1])

    matriculas_ativas = Matricula.objects.select_related('aluno').filter(
        status='ativa',
        aluno__status='ativo',
        data_inicio__lte=fim_mes,
    ).filter(
        Q(data_fim__isnull=True) | Q(data_fim__gte=inicio_mes)
    )

    totais_por_aluno = {}
    vencimentos_por_aluno = {}

    for matricula in matriculas_ativas:
        valor_calculado = matricula.calcular_valor_cobranca()
        if matricula.valor_mensalidade != valor_calculado:
            matricula.valor_mensalidade = valor_calculado
            matricula.save(update_fields=['valor_mensalidade', 'atualizado_em'])

        dia_base = min(max(matricula.dia_vencimento, 1), monthrange(ano, mes)[1])
        vencimento_padrao = date(ano, mes, dia_base)
        if (
            matricula.data_inicio.year == ano
            and matricula.data_inicio.month == mes
            and matricula.data_inicio > vencimento_padrao
        ):
            vencimento_matricula = matricula.data_inicio
        else:
            vencimento_matricula = vencimento_padrao

        totais_por_aluno.setdefault(matricula.aluno_id, Decimal('0'))
        totais_por_aluno[matricula.aluno_id] += valor_calculado
        atual = vencimentos_por_aluno.get(matricula.aluno_id)
        vencimentos_por_aluno[matricula.aluno_id] = max(atual, vencimento_matricula) if atual else vencimento_matricula

    if not totais_por_aluno:
        return 0

    criadas = 0
    for aluno_id, valor_total in totais_por_aluno.items():
        data_vencimento = vencimentos_por_aluno[aluno_id]
        mensalidade, criada = Mensalidade.objects.get_or_create(
            aluno_id=aluno_id,
            mes=mes,
            ano=ano,
            defaults={
                'valor_total': valor_total,
                'data_vencimento': data_vencimento,
            },
        )

        if criada:
            criadas += 1
            continue

        # Ajusta valores automaticamente quando ainda não há pagamento lançado.
        if mensalidade.valor_pago == 0 and mensalidade.status in ('pendente', 'vencida'):
            alterou = False
            if mensalidade.valor_total != valor_total:
                mensalidade.valor_total = valor_total
                alterou = True
            if mensalidade.data_vencimento != data_vencimento:
                mensalidade.data_vencimento = data_vencimento
                alterou = True
            if alterou:
                mensalidade.atualizar_status()
                mensalidade.save(update_fields=['valor_total', 'data_vencimento', 'status', 'atualizado_em'])

    return criadas


def atualizar_status_mensalidades_vencidas(referencia=None):
    hoje = referencia or date.today()
    atualizadas = 0

    mensalidades = Mensalidade.objects.filter(status='pendente', data_vencimento__lt=hoje)
    for mensalidade in mensalidades:
        mensalidade.atualizar_status()
        mensalidade.save(update_fields=['status', 'atualizado_em'])
        atualizadas += 1

    return atualizadas


def processar_rotina_financeira(mes, ano, referencia=None):
    criadas = gerar_cobrancas_do_mes(mes, ano)
    atualizadas = atualizar_status_mensalidades_vencidas(referencia=referencia)
    return criadas, atualizadas
