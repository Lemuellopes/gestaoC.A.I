from django.db import models
from django.utils import timezone
from datetime import date


class Responsavel(models.Model):
    nome = models.CharField(max_length=150, verbose_name='Nome Completo')
    cpf = models.CharField(max_length=14, unique=True, verbose_name='CPF')
    rg = models.CharField(max_length=20, blank=True, verbose_name='RG')
    telefone = models.CharField(max_length=20, verbose_name='Telefone')
    telefone_emergencia = models.CharField(max_length=20, blank=True, verbose_name='Tel. Emergência')
    email = models.EmailField(blank=True, verbose_name='E-mail')
    parentesco = models.CharField(
        max_length=30,
        choices=[
            ('mae', 'Mãe'), ('pai', 'Pai'), ('avo', 'Avó/Avô'),
            ('tio', 'Tio/Tia'), ('responsavel', 'Responsável Legal'), ('outro', 'Outro'),
        ],
        default='mae',
        verbose_name='Parentesco'
    )
    cep = models.CharField(max_length=9, blank=True, verbose_name='CEP')
    logradouro = models.CharField(max_length=200, blank=True, verbose_name='Logradouro')
    numero = models.CharField(max_length=10, blank=True, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=100, blank=True, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, default='Araripina', verbose_name='Cidade')
    estado = models.CharField(max_length=2, default='PE', verbose_name='Estado')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Responsável'
        verbose_name_plural = 'Responsáveis'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_parentesco_display()})"


class Aluno(models.Model):
    FAIXA_ETARIA_CHOICES = [
        ('bebe', 'Bebê (0-2 anos)'),
        ('toddler', 'Toddler (2-4 anos)'),
        ('kids', 'Kids (4-6 anos)'),
    ]
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('trancado', 'Trancado'),
    ]

    matricula = models.CharField(max_length=20, unique=True, verbose_name='Matrícula')
    nome = models.CharField(max_length=150, verbose_name='Nome Completo')
    data_nascimento = models.DateField(verbose_name='Data de Nascimento')
    faixa_etaria = models.CharField(
        max_length=20, choices=FAIXA_ETARIA_CHOICES, verbose_name='Faixa Etária'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ativo', verbose_name='Status'
    )
    responsavel_principal = models.ForeignKey(
        Responsavel, on_delete=models.PROTECT,
        related_name='alunos_principal', verbose_name='Responsável Principal'
    )
    responsavel_secundario = models.ForeignKey(
        Responsavel, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='alunos_secundario',
        verbose_name='Responsável Secundário'
    )
    # Informações médicas
    tipo_sanguineo = models.CharField(max_length=5, blank=True, verbose_name='Tipo Sanguíneo')
    alergias = models.TextField(blank=True, verbose_name='Alergias')
    medicamentos = models.TextField(blank=True, verbose_name='Medicamentos em uso')
    condicoes_especiais = models.TextField(blank=True, verbose_name='Condições Especiais')
    plano_saude = models.CharField(max_length=100, blank=True, verbose_name='Plano de Saúde')
    # Autorizações
    autorizacao_foto = models.BooleanField(default=False, verbose_name='Autoriza uso de foto')
    autorizacao_saida = models.BooleanField(default=False, verbose_name='Autoriza saída sozinho')
    # Documentos
    foto = models.ImageField(upload_to='alunos/fotos/', null=True, blank=True, verbose_name='Foto')
    documento = models.FileField(
        upload_to='alunos/docs/', null=True, blank=True, verbose_name='Documento'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    data_matricula = models.DateField(default=date.today, verbose_name='Data de Matrícula')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - {self.matricula}"

    def save(self, *args, **kwargs):
        if not self.matricula:
            ultimo = Aluno.objects.order_by('-id').first()
            num = (ultimo.id + 1) if ultimo else 1
            self.matricula = f"CAI{num:04d}"
        if not self.faixa_etaria:
            self.faixa_etaria = self._calcular_faixa()
        super().save(*args, **kwargs)

    def _calcular_faixa(self):
        idade = self.calcular_idade()
        if idade <= 2:
            return 'bebe'
        elif idade <= 4:
            return 'toddler'
        return 'kids'

    def calcular_idade(self):
        hoje = date.today()
        nascimento = self.data_nascimento
        return (
            hoje.year - nascimento.year
            - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        )

    @property
    def idade(self):
        return self.calcular_idade()

    @property
    def aniversario_no_mes(self):
        return self.data_nascimento.month == date.today().month
