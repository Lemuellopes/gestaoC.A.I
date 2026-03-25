from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Professor, HorarioDisponibilidade
from .forms import ProfessorForm, HorarioFormSet


@login_required
def lista_professores(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', 'ativo')
    especialidade = request.GET.get('especialidade', '')

    professores = Professor.objects.all()
    if status:
        professores = professores.filter(status=status)
    if especialidade:
        professores = professores.filter(especialidade=especialidade)
    if q:
        professores = professores.filter(
            Q(nome__icontains=q) | Q(cpf__icontains=q) | Q(email__icontains=q)
        )

    ativos = Professor.objects.filter(status='ativo').count()
    afastados = Professor.objects.filter(status='afastado').count()
    desligados = Professor.objects.filter(status='desligado').count()

    context = {
        'professores': professores,
        'q': q,
        'status': status,
        'especialidade': especialidade,
        'ativos': ativos,
        'afastados': afastados,
        'desligados': desligados,
    }
    return render(request, 'professores/lista.html', context)


@login_required
def perfil_professor(request, pk):
    professor = get_object_or_404(Professor, pk=pk)
    turmas = professor.turmas_responsavel.filter(status='ativa')
    turmas_aux = professor.turmas_auxiliar.filter(status='ativa')
    horarios = professor.horarios.all().order_by('dia_semana', 'hora_inicio')

    context = {
        'professor': professor,
        'turmas': turmas,
        'turmas_aux': turmas_aux,
        'horarios': horarios,
    }
    return render(request, 'professores/perfil.html', context)


@login_required
def novo_professor(request):
    if request.method == 'POST':
        form = ProfessorForm(request.POST, request.FILES)
        if form.is_valid():
            professor = form.save()
            messages.success(request, f'Professor(a) {professor.nome} cadastrado(a)!')
            return redirect('perfil_professor', pk=professor.pk)
    else:
        form = ProfessorForm()
    return render(request, 'professores/form.html', {'form': form, 'titulo': 'Novo Instrutor'})


@login_required
def editar_professor(request, pk):
    professor = get_object_or_404(Professor, pk=pk)
    if request.method == 'POST':
        form = ProfessorForm(request.POST, request.FILES, instance=professor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados atualizados!')
            return redirect('perfil_professor', pk=professor.pk)
    else:
        form = ProfessorForm(instance=professor)
    return render(request, 'professores/form.html', {
        'form': form, 'titulo': 'Editar Instrutor', 'professor': professor
    })
