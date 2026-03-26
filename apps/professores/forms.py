from django import forms
from django.forms import inlineformset_factory
from .models import Professor, HorarioDisponibilidade


class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'logradouro': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2}),
            'especialidade': forms.Select(attrs={'class': 'form-select'}),
            'formacao': forms.TextInput(attrs={'class': 'form-control'}),
            'registro_cref': forms.TextInput(attrs={'class': 'form-control'}),
            'anos_experiencia': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
            'salario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_admissao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'data_desligamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_nascimento'].input_formats = ['%Y-%m-%d']
        self.fields['data_admissao'].input_formats = ['%Y-%m-%d']
        self.fields['data_desligamento'].input_formats = ['%Y-%m-%d']
        self.fields['data_desligamento'].required = False
        self.fields['salario'].required = False


HorarioFormSet = inlineformset_factory(
    Professor, HorarioDisponibilidade,
    fields=('dia_semana', 'hora_inicio', 'hora_fim'),
    extra=1, can_delete=True,
    widgets={
        'dia_semana': forms.Select(attrs={'class': 'form-select'}),
        'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        'hora_fim': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
    }
)
