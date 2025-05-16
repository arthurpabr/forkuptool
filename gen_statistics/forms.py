from django import forms

class GerarEstatisticasForm(forms.Form):

	def __init__(self, configuracao_choices, *args, **kwargs):
		super(GerarEstatisticasForm, self).__init__(*args, **kwargs)
		self.fields['configuracao_escolhida'].choices = configuracao_choices

	configuracao_escolhida = forms.ChoiceField(label='Escolha uma configuração', label_suffix=': ', \
		required=True, choices=(), widget=forms.Select(attrs={'style':'width: 800px;'}))