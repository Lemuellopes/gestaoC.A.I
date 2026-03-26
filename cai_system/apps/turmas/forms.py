from django import forms
from .models import Turma, Matricula


class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'faixa_etaria': forms.Select(attrs={'class': 'form-select'}),
            'dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'horario_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'horario_fim': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'capacidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'professor_responsavel': forms.Select(attrs={'class': 'form-select'}),
            'professores_auxiliares': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.required and isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.NumberInput, forms.EmailInput, forms.DateInput)):
                field.widget.attrs.setdefault('placeholder', 'Opcional')


class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = ('aluno', 'status', 'data_inicio', 'plano', 'frequencia_semanal', 'dia_vencimento', 'observacoes')
        widgets = {
            'aluno': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'plano': forms.Select(attrs={'class': 'form-select'}),
            'frequencia_semanal': forms.Select(attrs={'class': 'form-select'}),
            'dia_vencimento': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 28}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_inicio'].input_formats = ['%Y-%m-%d']
        self.fields['plano'].help_text = (
            'Semestral: 1x R$ 94,90 | 2x R$ 154,90. '
            'Anual: 1x R$ 89,90 | 2x R$ 149,90.'
        )
        for field_name, field in self.fields.items():
            if not field.required and isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.NumberInput, forms.EmailInput, forms.DateInput)):
                field.widget.attrs.setdefault('placeholder', 'Opcional')
