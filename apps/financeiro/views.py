from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from datetime import date
from decimal import Decimal
from .models import Mensalidade, Pagamento
from apps.alunos.models import Aluno
from .forms import MensalidadeForm, PagamentoForm


@login_required
def dashboard_financeiro(request):
    hoje = date.today()
    mes = int(request.GET.get('mes', hoje.month))
    ano = int(request.GET.get('ano', hoje.year))

    mensalidades_mes = Mensalidade.objects.filter(mes=mes, ano=ano)

    recebido = mensalidades_mes.filter(status='paga').aggregate(
        total=Sum('valor_pago'))['total'] or Decimal('0')
    total_a_receber = mensalidades_mes.exclude(status='cancelada').aggregate(
        total=Sum('valor_total'))['total'] or Decimal('0')
    pendente_vencido = Mensalidade.objects.filter(status='vencida').aggregate(
        total=Sum('valor_total'))['total'] or Decimal('0')

    total = mensalidades_mes.exclude(status='cancelada').count()
    pagas = mensalidades_mes.filter(status='paga').count()
    inadimplentes = Aluno.objects.filter(
        status='ativo',
        mensalidades__status__in=['vencida', 'pendente'],
        mensalidades__mes=mes,
        mensalidades__ano=ano
    ).distinct().count()

    taxa_adimplencia = round((pagas / total * 100) if total > 0 else 0, 1)

    mensalidades_vencidas = Mensalidade.objects.filter(
        status='vencida'
    ).select_related('aluno').order_by('data_vencimento')

    pagamentos_recentes = Pagamento.objects.select_related(
        'mensalidade__aluno', 'registrado_por'
    ).order_by('-criado_em')[:15]

    # Resumo últimos 6 meses
    resumo_meses = []
    for i in range(5, -1, -1):
        m = mes - i
        a = ano
        while m <= 0:
            m += 12
            a -= 1
        dados = Mensalidade.objects.filter(mes=m, ano=a)
        rec = dados.filter(status='paga').aggregate(total=Sum('valor_pago'))['total'] or 0
        resumo_meses.append({
            'mes': m, 'ano': a,
            'recebido': float(rec),
            'nome': ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][m-1]
        })

    context = {
        'mes': mes, 'ano': ano,
        'recebido': recebido,
        'total_a_receber': total_a_receber,
        'pendente_vencido': pendente_vencido,
        'taxa_adimplencia': taxa_adimplencia,
        'inadimplentes': inadimplentes,
        'mensalidades_vencidas': mensalidades_vencidas,
        'pagamentos_recentes': pagamentos_recentes,
        'resumo_meses': resumo_meses,
        'meses_choices': Mensalidade.MES_CHOICES,
    }
    return render(request, 'financeiro/dashboard.html', context)


@login_required
def lista_mensalidades(request):
    mes = int(request.GET.get('mes', date.today().month))
    ano = int(request.GET.get('ano', date.today().year))
    status = request.GET.get('status', '')
    q = request.GET.get('q', '')

    mensalidades = Mensalidade.objects.select_related('aluno').filter(mes=mes, ano=ano)
    if status:
        mensalidades = mensalidades.filter(status=status)
    if q:
        mensalidades = mensalidades.filter(aluno__nome__icontains=q)

    context = {
        'mensalidades': mensalidades,
        'mes': mes, 'ano': ano, 'status': status, 'q': q,
        'meses_choices': Mensalidade.MES_CHOICES,
        'status_choices': Mensalidade.STATUS_CHOICES,
    }
    return render(request, 'financeiro/mensalidades.html', context)


@login_required
def nova_mensalidade(request):
    if request.method == 'POST':
        form = MensalidadeForm(request.POST)
        if form.is_valid():
            mensalidade = form.save()
            messages.success(request, 'Mensalidade criada!')
            return redirect('lista_mensalidades')
    else:
        form = MensalidadeForm()
    return render(request, 'financeiro/mensalidade_form.html', {'form': form})


@login_required
def registrar_pagamento(request, mensalidade_pk):
    mensalidade = get_object_or_404(Mensalidade, pk=mensalidade_pk)
    if request.method == 'POST':
        form = PagamentoForm(request.POST, request.FILES)
        if form.is_valid():
            pagamento = form.save(commit=False)
            pagamento.mensalidade = mensalidade
            pagamento.registrado_por = request.user
            pagamento.save()
            messages.success(request, f'Pagamento de R$ {pagamento.valor} registrado!')
            return redirect('lista_mensalidades')
    else:
        pendente = mensalidade.valor_pendente
        form = PagamentoForm(initial={'valor': pendente})
    return render(request, 'financeiro/pagamento_form.html', {
        'form': form, 'mensalidade': mensalidade
    })
