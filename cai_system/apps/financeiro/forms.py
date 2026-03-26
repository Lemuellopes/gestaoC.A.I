from django import forms
from .models import Mensalidade, Pagamento


class MensalidadeForm(forms.ModelForm):
    class Meta:
        model = Mensalidade
        fields = ('aluno', 'mes', 'ano', 'valor_total', 'data_vencimento', 'desconto', 'observacoes')
        widgets = {
            'aluno': forms.Select(attrs={'class': 'form-select'}),
            'mes': forms.Select(attrs={'class': 'form-select'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_vencimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'desconto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_vencimento'].input_formats = ['%Y-%m-%d']
        for field_name, field in self.fields.items():
            if not field.required and isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.NumberInput, forms.EmailInput, forms.DateInput)):
                field.widget.attrs.setdefault('placeholder', 'Opcional')


class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ('valor', 'forma_pagamento', 'data_pagamento', 'comprovante', 'observacoes')
        widgets = {
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-select'}),
            'data_pagamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_pagamento'].input_formats = ['%Y-%m-%d']
        for field_name, field in self.fields.items():
            if not field.required and isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.NumberInput, forms.EmailInput, forms.DateInput)):
                field.widget.attrs.setdefault('placeholder', 'Opcional')
