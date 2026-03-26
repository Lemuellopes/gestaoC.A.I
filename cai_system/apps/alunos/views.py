from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from datetime import date
from .models import Aluno, Responsavel
from apps.financeiro.models import Mensalidade, Pagamento
from apps.turmas.models import Matricula
from .forms import AlunoForm, ResponsavelForm


@login_required
def lista_alunos(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', 'ativo')
    faixa = request.GET.get('faixa', '')

    alunos = Aluno.objects.select_related('responsavel_principal').all()

    if status:
        alunos = alunos.filter(status=status)
    if faixa:
        alunos = alunos.filter(faixa_etaria=faixa)
    if q:
        alunos = alunos.filter(
            Q(nome__icontains=q) |
            Q(matricula__icontains=q) |
            Q(responsavel_principal__nome__icontains=q)
        )

    aniversariantes = Aluno.objects.filter(
        status='ativo', data_nascimento__month=date.today().month
    ).order_by('data_nascimento__day')

    context = {
        'alunos': alunos,
        'aniversariantes': aniversariantes,
        'q': q,
        'status': status,
        'faixa': faixa,
        'total': alunos.count(),
    }
    return render(request, 'alunos/lista.html', context)


@login_required
def perfil_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    matriculas = aluno.matriculas.select_related('turma', 'turma__professor_responsavel').all()
    mensalidades = aluno.mensalidades.all().order_by('-ano', '-mes')

    context = {
        'aluno': aluno,
        'matriculas': matriculas,
        'mensalidades': mensalidades,
    }
    return render(request, 'alunos/perfil.html', context)


@login_required
def novo_aluno(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST, request.FILES, incluir_matricula=True)
        if form.is_valid():
            with transaction.atomic():
                aluno = form.save()

                if form.cleaned_data.get('criar_matricula'):
                    matricula = Matricula(
                        aluno=aluno,
                        turma=form.cleaned_data['turma_matricula'],
                        status='ativa',
                        data_inicio=form.cleaned_data['data_inicio_matricula'],
                        plano=form.cleaned_data['plano_matricula'],
                        frequencia_semanal=int(form.cleaned_data['frequencia_matricula']),
                        dia_vencimento=form.cleaned_data['dia_vencimento_matricula'],
                        cobranca_personalizada=form.cleaned_data.get('cobranca_personalizada', False),
                        valor_personalizado=form.cleaned_data.get('valor_personalizado_matricula'),
                        observacoes=form.cleaned_data.get('observacoes_matricula') or '',
                    )
                    matricula.save()

            messages.success(request, f'Aluno {aluno.nome} cadastrado com sucesso!')
            return redirect('perfil_aluno', pk=aluno.pk)
    else:
        form = AlunoForm(incluir_matricula=True)
    return render(request, 'alunos/form.html', {'form': form, 'titulo': 'Novo Aluno'})


@login_required
def editar_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == 'POST':
        form = AlunoForm(request.POST, request.FILES, instance=aluno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('perfil_aluno', pk=aluno.pk)
    else:
        form = AlunoForm(instance=aluno)
    return render(request, 'alunos/form.html', {'form': form, 'titulo': 'Editar Aluno', 'aluno': aluno})


@login_required
def novo_responsavel(request):
    if request.method == 'POST':
        form = ResponsavelForm(request.POST)
        if form.is_valid():
            responsavel = form.save()
            messages.success(request, f'Responsável {responsavel.nome} cadastrado!')
            next_url = request.GET.get('next', 'lista_alunos')
            return redirect(next_url)
    else:
        form = ResponsavelForm()
    return render(request, 'alunos/responsavel_form.html', {'form': form})


@login_required
def registrar_pagamento_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    mensalidades_pendentes = aluno.mensalidades.filter(
        status__in=['pendente', 'vencida', 'parcial']
    )
    if request.method == 'POST':
        mensalidade_id = request.POST.get('mensalidade')
        valor = request.POST.get('valor')
        forma = request.POST.get('forma_pagamento')
        if mensalidade_id and valor:
            mensalidade = get_object_or_404(Mensalidade, pk=mensalidade_id, aluno=aluno)
            Pagamento.objects.create(
                mensalidade=mensalidade,
                valor=valor,
                forma_pagamento=forma,
                registrado_por=request.user
            )
            messages.success(request, 'Pagamento registrado com sucesso!')
            return redirect('perfil_aluno', pk=aluno.pk)
    return render(request, 'alunos/pagamento.html', {
        'aluno': aluno,
        'mensalidades_pendentes': mensalidades_pendentes,
    })
