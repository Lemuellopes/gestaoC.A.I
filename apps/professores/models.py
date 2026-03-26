from django.db import models
from datetime import date


class Professor(models.Model):
    ESPECIALIDADE_CHOICES = [
        ('natacao_infantil', 'Natação Infantil'),
        ('bebe_conforto', 'Bebê Conforto'),
        ('auto_salvamento', 'Auto Salvamento'),
        ('hidroginastica', 'Hidroginástica'),
        ('geral', 'Geral'),
    ]
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('afastado', 'Afastado'),
        ('desligado', 'Desligado'),
    ]
    TIPO_CONTRATO_CHOICES = [
        ('clt', 'CLT'),
        ('pj', 'PJ'),
        ('autonomo', 'Autônomo'),
        ('voluntario', 'Voluntário'),
    ]

    nome = models.CharField(max_length=150, verbose_name='Nome Completo')
    cpf = models.CharField(max_length=14, unique=True, verbose_name='CPF')
    rg = models.CharField(max_length=20, blank=True, verbose_name='RG')
    data_nascimento = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')
    telefone = models.CharField(max_length=20, verbose_name='Telefone')
    email = models.EmailField(blank=True, verbose_name='E-mail')
    # Endereço
    cep = models.CharField(max_length=9, blank=True, verbose_name='CEP')
    logradouro = models.CharField(max_length=200, blank=True, verbose_name='Logradouro')
    numero = models.CharField(max_length=10, blank=True, verbose_name='Número')
    bairro = models.CharField(max_length=100, blank=True, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, default='Araripina', verbose_name='Cidade')
    estado = models.CharField(max_length=2, default='PE', verbose_name='Estado')
    # Profissional
    especialidade = models.CharField(
        max_length=30, choices=ESPECIALIDADE_CHOICES, default='natacao_infantil',
        verbose_name='Especialidade'
    )
    formacao = models.CharField(max_length=200, blank=True, verbose_name='Formação')
    registro_cref = models.CharField(max_length=30, blank=True, verbose_name='CREF')
    anos_experiencia = models.PositiveIntegerField(default=0, verbose_name='Anos de Experiência')
    tipo_contrato = models.CharField(
        max_length=20, choices=TIPO_CONTRATO_CHOICES, default='clt',
        verbose_name='Tipo de Contrato'
    )
    salario = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Salário/Valor'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ativo', verbose_name='Status'
    )
    data_admissao = models.DateField(default=date.today, verbose_name='Data de Admissão')
    data_desligamento = models.DateField(null=True, blank=True, verbose_name='Data de Desligamento')
    foto = models.ImageField(
        upload_to='professores/fotos/', null=True, blank=True, verbose_name='Foto'
    )
    bio = models.TextField(blank=True, verbose_name='Biografia/Observações')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Professor/Instrutor'
        verbose_name_plural = 'Professores/Instrutores'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - {self.get_especialidade_display()}"

    @property
    def tempo_de_casa(self):
        ref = self.data_desligamento or date.today()
        delta = ref - self.data_admissao
        anos = delta.days // 365
        meses = (delta.days % 365) // 30
        if anos > 0:
            return f"{anos} ano(s) e {meses} mês(es)"
        return f"{meses} mês(es)"

    @property
    def idade(self):
        if not self.data_nascimento:
            return None
        hoje = date.today()
        return (
            hoje.year - self.data_nascimento.year
            - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        )


class HorarioDisponibilidade(models.Model):
    DIA_CHOICES = [
        (0, 'Segunda-feira'), (1, 'Terça-feira'), (2, 'Quarta-feira'),
        (3, 'Quinta-feira'), (4, 'Sexta-feira'), (5, 'Sábado'), (6, 'Domingo'),
    ]

    professor = models.ForeignKey(
        Professor, on_delete=models.CASCADE,
        related_name='horarios', verbose_name='Professor'
    )
    dia_semana = models.IntegerField(choices=DIA_CHOICES, verbose_name='Dia da Semana')
    hora_inicio = models.TimeField(verbose_name='Início')
    hora_fim = models.TimeField(verbose_name='Fim')

    class Meta:
        verbose_name = 'Horário de Disponibilidade'
        verbose_name_plural = 'Horários de Disponibilidade'
        ordering = ['dia_semana', 'hora_inicio']

    def __str__(self):
        return (
            f"{self.professor.nome} - {self.get_dia_semana_display()} "
            f"{self.hora_inicio:%H:%M}-{self.hora_fim:%H:%M}"
        )
