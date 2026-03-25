from django.db import models
from apps.alunos.models import Aluno
from apps.professores.models import Professor


class Turma(models.Model):
    DIA_SEMANA_CHOICES = [
        (0, 'Segunda'), (1, 'Terça'), (2, 'Quarta'),
        (3, 'Quinta'), (4, 'Sexta'), (5, 'Sábado'),
    ]
    FAIXA_ETARIA_CHOICES = [
        ('bebe', 'Bebê (0-2 anos)'),
        ('toddler', 'Toddler (2-4 anos)'),
        ('kids', 'Kids (4-6 anos)'),
        ('mista', 'Turma Mista'),
    ]
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('inativa', 'Inativa'),
        ('encerrada', 'Encerrada'),
    ]

    nome = models.CharField(max_length=100, verbose_name='Nome da Turma')
    faixa_etaria = models.CharField(
        max_length=20, choices=FAIXA_ETARIA_CHOICES, verbose_name='Faixa Etária'
    )
    dia_semana = models.IntegerField(choices=DIA_SEMANA_CHOICES, verbose_name='Dia da Semana')
    horario_inicio = models.TimeField(verbose_name='Horário de Início')
    horario_fim = models.TimeField(verbose_name='Horário de Fim')
    capacidade = models.PositiveIntegerField(default=10, verbose_name='Capacidade Máxima')
    professor_responsavel = models.ForeignKey(
        Professor, on_delete=models.PROTECT,
        related_name='turmas_responsavel', verbose_name='Professor Responsável'
    )
    professores_auxiliares = models.ManyToManyField(
        Professor, blank=True,
        related_name='turmas_auxiliar', verbose_name='Professores Auxiliares'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ativa', verbose_name='Status'
    )
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        ordering = ['dia_semana', 'horario_inicio']

    def __str__(self):
        return (
            f"{self.nome} - {self.get_dia_semana_display()} "
            f"{self.horario_inicio:%H:%M}"
        )

    @property
    def vagas_disponiveis(self):
        matriculas_ativas = self.matriculas.filter(status='ativa').count()
        return max(0, self.capacidade - matriculas_ativas)

    @property
    def total_alunos(self):
        return self.matriculas.filter(status='ativa').count()

    @property
    def percentual_ocupacao(self):
        if self.capacidade == 0:
            return 0
        return round((self.total_alunos / self.capacidade) * 100, 1)


class Matricula(models.Model):
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('pausada', 'Pausada'),
        ('cancelada', 'Cancelada'),
    ]

    aluno = models.ForeignKey(
        Aluno, on_delete=models.PROTECT,
        related_name='matriculas', verbose_name='Aluno'
    )
    turma = models.ForeignKey(
        Turma, on_delete=models.PROTECT,
        related_name='matriculas', verbose_name='Turma'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ativa', verbose_name='Status'
    )
    data_inicio = models.DateField(verbose_name='Data de Início')
    data_fim = models.DateField(null=True, blank=True, verbose_name='Data de Fim')
    valor_mensalidade = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, verbose_name='Valor da Mensalidade (R$)'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        ordering = ['-data_inicio']
        constraints = [
            models.UniqueConstraint(
                fields=['aluno', 'turma'],
                condition=models.Q(status='ativa'),
                name='unique_matricula_ativa_por_turma'
            )
        ]

    def __str__(self):
        return f"{self.aluno.nome} → {self.turma.nome} ({self.get_status_display()})"
