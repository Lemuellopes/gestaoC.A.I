from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from decimal import Decimal

from apps.alunos.models import Aluno
from apps.professores.models import Professor
from apps.turmas.models import Turma, Matricula
from apps.financeiro.models import Mensalidade, Pagamento


@login_required
def home(request):
    hoje = date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year

    # KPIs de alunos
    total_alunos = Aluno.objects.filter(status='ativo').count()
    aniversariantes = Aluno.objects.filter(
        status='ativo', data_nascimento__month=mes_atual
    ).order_by('data_nascimento__day')

    # KPIs de professores
    total_professores = Professor.objects.filter(status='ativo').count()
    dia_semana_hoje = hoje.weekday()
    professores_hoje = Professor.objects.filter(
        status='ativo',
        horarios__dia_semana=dia_semana_hoje
    ).distinct()

    # KPIs de turmas
    total_turmas = Turma.objects.filter(status='ativa').count()
    turmas_hoje = Turma.objects.filter(
        status='ativa', dia_semana=dia_semana_hoje
    ).select_related('professor_responsavel')

    # Cálculo de ocupação média
    turmas_ativas = Turma.objects.filter(status='ativa')
    if turmas_ativas.exists():
        total_cap = sum(t.capacidade for t in turmas_ativas)
        total_alunos_turmas = sum(t.total_alunos for t in turmas_ativas)
        taxa_ocupacao = round((total_alunos_turmas / total_cap * 100) if total_cap > 0 else 0, 1)
    else:
        taxa_ocupacao = 0

    # KPIs financeiros
    mensalidades_mes = Mensalidade.objects.filter(mes=mes_atual, ano=ano_atual)
    recebido_mes = mensalidades_mes.filter(status='paga').aggregate(
        total=Sum('valor_pago')
    )['total'] or Decimal('0')
    total_a_receber = mensalidades_mes.exclude(status='cancelada').aggregate(
        total=Sum('valor_total')
    )['total'] or Decimal('0')
    pendentes_vencidos = Mensalidade.objects.filter(
        status='vencida'
    ).count()

    total_mensalidades = mensalidades_mes.exclude(status='cancelada').count()
    pagas = mensalidades_mes.filter(status='paga').count()
    taxa_adimplencia = round((pagas / total_mensalidades * 100) if total_mensalidades > 0 else 0, 1)

    # Mensalidades vencidas
    mensalidades_vencidas = Mensalidade.objects.filter(
        status='vencida'
    ).select_related('aluno').order_by('data_vencimento')[:10]

    # Vencimentos próximos (próximos 5 dias)
    prazo = hoje + timedelta(days=5)
    vencimentos_proximos = Mensalidade.objects.filter(
        status='pendente',
        data_vencimento__gte=hoje,
        data_vencimento__lte=prazo
    ).select_related('aluno').order_by('data_vencimento')[:8]

    # Pagamentos recentes
    pagamentos_recentes = Pagamento.objects.select_related(
        'mensalidade__aluno', 'registrado_por'
    ).order_by('-criado_em')[:8]

    # Receita vs mês anterior
    mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
    ano_anterior_ref = ano_atual if mes_atual > 1 else ano_atual - 1
    recebido_mes_anterior = Mensalidade.objects.filter(
        mes=mes_anterior, ano=ano_anterior_ref, status='paga'
    ).aggregate(total=Sum('valor_pago'))['total'] or Decimal('0')

    variacao_receita = 0
    if recebido_mes_anterior > 0:
        variacao_receita = round(
            float((recebido_mes - recebido_mes_anterior) / recebido_mes_anterior * 100), 1
        )

    context = {
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_turmas': total_turmas,
        'taxa_ocupacao': taxa_ocupacao,
        'recebido_mes': recebido_mes,
        'total_a_receber': total_a_receber,
        'pendentes_vencidos': pendentes_vencidos,
        'taxa_adimplencia': taxa_adimplencia,
        'variacao_receita': variacao_receita,
        'aniversariantes': aniversariantes[:6],
        'turmas_hoje': turmas_hoje,
        'professores_hoje': professores_hoje,
        'mensalidades_vencidas': mensalidades_vencidas,
        'vencimentos_proximos': vencimentos_proximos,
        'pagamentos_recentes': pagamentos_recentes,
        'hoje': hoje,
        'mes_nome': hoje.strftime('%B'),
    }
    return render(request, 'dashboard/home.html', context)
