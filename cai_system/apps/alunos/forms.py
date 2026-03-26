from django import forms
from .models import Aluno, Responsavel
from apps.turmas.models import Matricula, Turma


class ResponsavelForm(forms.ModelForm):
    class Meta:
        model = Responsavel
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone_emergencia': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'parentesco': forms.Select(attrs={'class': 'form-select'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'logradouro': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['logradouro'].label = 'Rua'
        if not self.is_bound and (not self.instance or not self.instance.pk):
            self.fields['cidade'].initial = 'Santa Cruz do Capibaribe'

        for field_name, field in self.fields.items():
            if not field.required:
                if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.NumberInput, forms.EmailInput, forms.DateInput)):
                    field.widget.attrs.setdefault('placeholder', 'Opcional')


class AlunoForm(forms.ModelForm):
    criar_matricula = forms.BooleanField(
        required=False,
        initial=True,
        label='Criar matrícula agora',
    )
    turma_matricula = forms.ModelChoiceField(
        queryset=Turma.objects.filter(status='ativa').order_by('dia_semana', 'horario_inicio'),
        required=False,
        label='Turma da matrícula',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    data_inicio_matricula = forms.DateField(
        required=False,
        label='Data de início da matrícula',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
    )
    plano_matricula = forms.ChoiceField(
        choices=Matricula.PLANO_CHOICES,
        required=False,
        label='Plano',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    frequencia_matricula = forms.ChoiceField(
        choices=Matricula.FREQUENCIA_SEMANAL_CHOICES,
        required=False,
        label='Frequência semanal',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    dia_vencimento_matricula = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=28,
        initial=10,
        label='Dia de vencimento',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 28}),
    )
    cobranca_personalizada = forms.BooleanField(
        required=False,
        label='Usar valor personalizado (desconto/bolsista)',
    )
    valor_personalizado_matricula = forms.DecimalField(
        required=False,
        max_digits=8,
        decimal_places=2,
        min_value=0,
        label='Valor personalizado (R$)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    )
    observacoes_matricula = forms.CharField(
        required=False,
        label='Observações da matrícula',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
    )

    class Meta:
        model = Aluno
        exclude = ('matricula', 'tipo_sanguineo', 'alergias', 'plano_saude')
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'
            ),
            'faixa_etaria': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'responsavel_principal': forms.Select(attrs={'class': 'form-select'}),
            'responsavel_secundario': forms.Select(attrs={'class': 'form-select'}),
            'medicamentos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'condicoes_especiais': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'data_matricula': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'
            ),
        }

    def __init__(self, *args, **kwargs):
        incluir_matricula = kwargs.pop('incluir_matricula', False)
        super().__init__(*args, **kwargs)
        self.fields['data_nascimento'].input_formats = ['%Y-%m-%d']
        self.fields['data_matricula'].input_formats = ['%Y-%m-%d']
        self.fields['plano_matricula'].help_text = (
            'Semestral: 1x R$ 94,90 | 2x R$ 154,90. '
            'Anual: 1x R$ 89,90 | 2x R$ 149,90.'
        )
        self.fields['valor_personalizado_matricula'].help_text = (
            'Use 0,00 para bolsista integral ou informe o valor com desconto.'
        )

        for field_name, field in self.fields.items():
            if not field.required:
                if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.NumberInput, forms.EmailInput, forms.DateInput)):
                    field.widget.attrs.setdefault('placeholder', 'Opcional')

        if incluir_matricula:
            self.order_fields([
                'nome', 'data_nascimento', 'faixa_etaria', 'status',
                'responsavel_principal', 'responsavel_secundario',
                'medicamentos', 'condicoes_especiais',
                'autorizacao_foto', 'autorizacao_saida', 'foto', 'documento',
                'observacoes', 'data_matricula',
                'criar_matricula', 'turma_matricula', 'data_inicio_matricula',
                'plano_matricula', 'frequencia_matricula', 'dia_vencimento_matricula', 'cobranca_personalizada',
                'valor_personalizado_matricula', 'observacoes_matricula',
            ])
            return

        for field_name in [
            'criar_matricula', 'turma_matricula', 'data_inicio_matricula',
            'plano_matricula', 'frequencia_matricula', 'dia_vencimento_matricula', 'cobranca_personalizada',
            'valor_personalizado_matricula', 'observacoes_matricula',
        ]:
            self.fields.pop(field_name, None)

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('criar_matricula'):
            return cleaned_data

        if not cleaned_data.get('turma_matricula'):
            self.add_error('turma_matricula', 'Selecione uma turma para criar a matrícula.')
        if not cleaned_data.get('data_inicio_matricula'):
            self.add_error('data_inicio_matricula', 'Informe a data de início da matrícula.')
        if not cleaned_data.get('plano_matricula'):
            self.add_error('plano_matricula', 'Selecione o plano da matrícula.')
        if not cleaned_data.get('frequencia_matricula'):
            self.add_error('frequencia_matricula', 'Selecione a frequência semanal.')
        if not cleaned_data.get('dia_vencimento_matricula'):
            self.add_error('dia_vencimento_matricula', 'Informe o dia de vencimento da matrícula.')

        usa_personalizado = cleaned_data.get('cobranca_personalizada')
        valor_personalizado = cleaned_data.get('valor_personalizado_matricula')

        if usa_personalizado and valor_personalizado is None:
            self.add_error(
                'valor_personalizado_matricula',
                'Informe o valor personalizado para desconto/bolsista.'
            )

        return cleaned_data
