from django.db import models

class Recepcionista(models.Model):
	SEXO_CHOICES = (
		('M', 'Masculino'),
		('F', 'Feminino'),
	)
	nome = models.CharField(max_length=50, blank=False, unique=True)
	sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
	data_de_admissao = models.DateField(null=True)

	class Meta:
		verbose_name='Recepcionista'
		verbose_name_plural='Recepcionistas'

	def __str__(self):
		return self.nome
	
class Professor(models.Model):
	SEXO_CHOICES = (
		('M', 'Masculino'),
		('F', 'Feminino'),
	)
	nome = models.CharField(max_length=50, blank=False, unique=False)
	sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
	data_de_admissao = models.DateField(null=True)
	apelido = models.CharField(max_length=50, null=True, unique=True)

	class Meta:
		verbose_name='Professor'
		verbose_name_plural='Professores'

	def __str__(self):
		return self.nome
