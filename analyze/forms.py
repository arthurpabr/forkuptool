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


class SimularConflitosForm(forms.Form):

	def __init__(self, configuracaoferramenta_choices, *args, **kwargs):
		super(SimularConflitosForm, self).__init__(*args, **kwargs)
		self.fields['configuracaoferramenta_escolhida'].choices = configuracaoferramenta_choices

	configuracaoferramenta_escolhida = forms.ChoiceField(label='Escolha uma configuração', label_suffix=': ', \
		required=True, choices=(), widget=forms.Select(attrs={'style':'width: 350px;'}))
	nome_branch_forkeado = forms.CharField(max_length=50,label='Nome da branch do repositório forkeado')
	nome_branch_origem = forms.CharField(max_length=50,label='Nome da branch do repositório origem')
	apagar_branch_merge = forms.BooleanField(initial=False, required=True, label='Apagar branch de merge?')
