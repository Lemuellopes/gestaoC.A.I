from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Turma, Matricula
from .forms import TurmaForm, MatriculaForm


@login_required
def lista_turmas(request):
    status = request.GET.get('status', 'ativa')
    faixa = request.GET.get('faixa', '')

    turmas = Turma.objects.select_related('professor_responsavel').all()
    if status:
        turmas = turmas.filter(status=status)
    if faixa:
        turmas = turmas.filter(faixa_etaria=faixa)

    context = {
        'turmas': turmas,
        'status': status,
        'faixa': faixa,
        'DIA_CHOICES': Turma.DIA_SEMANA_CHOICES,
    }
    return render(request, 'turmas/lista.html', context)


@login_required
def detalhe_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    matriculas = turma.matriculas.select_related('aluno').filter(status='ativa')
    context = {'turma': turma, 'matriculas': matriculas}
    return render(request, 'turmas/detalhe.html', context)


@login_required
def nova_turma(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            turma = form.save()
            messages.success(request, f'Turma "{turma.nome}" criada com sucesso!')
            return redirect('detalhe_turma', pk=turma.pk)
    else:
        form = TurmaForm()
    return render(request, 'turmas/form.html', {'form': form, 'titulo': 'Nova Turma'})


@login_required
def editar_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    if request.method == 'POST':
        form = TurmaForm(request.POST, instance=turma)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma atualizada!')
            return redirect('detalhe_turma', pk=turma.pk)
    else:
        form = TurmaForm(instance=turma)
    return render(request, 'turmas/form.html', {'form': form, 'titulo': 'Editar Turma', 'turma': turma})


@login_required
def matricular_aluno(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    if request.method == 'POST':
        form = MatriculaForm(request.POST)
        if form.is_valid():
            matricula = form.save(commit=False)
            matricula.turma = turma
            try:
                matricula.save()
                messages.success(request, f'{matricula.aluno.nome} matriculado(a)!')
            except Exception as e:
                messages.error(request, f'Erro ao matricular: {e}')
            return redirect('detalhe_turma', pk=turma.pk)
    else:
        form = MatriculaForm(initial={'turma': turma})
    return render(request, 'turmas/matricula_form.html', {'form': form, 'turma': turma})
