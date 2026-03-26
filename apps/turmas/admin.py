from django.contrib import admin
from .models import Turma, Matricula


class MatriculaInline(admin.TabularInline):
    model = Matricula
    fields = ('aluno', 'status', 'data_inicio', 'valor_mensalidade')
    extra = 0
    show_change_link = True


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'faixa_etaria', 'dia_semana', 'horario_inicio',
        'professor_responsavel', 'capacidade', 'total_alunos', 'status'
    )
    list_filter = ('status', 'faixa_etaria', 'dia_semana')
    search_fields = ('nome',)
    filter_horizontal = ('professores_auxiliares',)
    inlines = [MatriculaInline]

    def total_alunos(self, obj):
        return obj.total_alunos
    total_alunos.short_description = 'Alunos'


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'turma', 'status', 'data_inicio', 'valor_mensalidade')
    list_filter = ('status', 'turma__faixa_etaria')
    search_fields = ('aluno__nome', 'turma__nome')
    raw_id_fields = ('aluno',)
