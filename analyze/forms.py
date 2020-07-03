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
