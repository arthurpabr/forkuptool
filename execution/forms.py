from django import forms

class ExecutarFerramentaForm(forms.Form):

	def __init__(self, configuracaoferramenta_choices, *args, **kwargs):
		super(ExecutarFerramentaForm, self).__init__(*args, **kwargs)
		self.fields['configuracaoferramenta_escolhida'].choices = configuracaoferramenta_choices

	configuracaoferramenta_escolhida = forms.ChoiceField(label='Escolha uma configuração para executar a ferramenta', label_suffix=': ', \
		required=True, choices=(), widget=forms.Select(attrs={'style':'width: 350px;'}))

