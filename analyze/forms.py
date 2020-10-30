from django import forms

class AnalisarTimelineForm(forms.Form):

	data_inicial = forms.DateField(
		required=True,
		label='Informe a data inicial',
		widget=forms.DateInput(format='%m/%d/%Y', attrs={'class': 'datepicker'})
	)

	data_final = forms.DateField(
		required=True,
		label='Informe a data final',
		widget=forms.DateInput(format='%m/%d/%Y', attrs={'class': 'datepicker'})
	)

	resumida = forms.BooleanField(
		required=False,
		label='Esconder a linha do tempo? '
	)


class CompararRepositoriosForm(forms.Form):

	def __init__(self, configuracaogeral_choices, *args, **kwargs):
		super(CompararRepositoriosForm, self).__init__(*args, **kwargs)
		self.fields['configuracaogeral_escolhida'].choices = configuracaogeral_choices

	configuracaogeral_escolhida = forms.ChoiceField(label='Escolha uma configuração', label_suffix=': ', \
		required=True, choices=(), widget=forms.Select(attrs={'style':'width: 350px;'}))


class VisualizarComparacaoRepositoriosForm(forms.Form):

	def __init__(self, comparacao_choices, *args, **kwargs):
		super(VisualizarComparacaoRepositoriosForm, self).__init__(*args, **kwargs)
		self.fields['comparacao_escolhida'].choices = comparacao_choices

	comparacao_escolhida = forms.ChoiceField(label='Escolha uma comparação para visualização', label_suffix=': ', \
		required=True, choices=(), widget=forms.Select(attrs={'style':'width: 350px;'}))


