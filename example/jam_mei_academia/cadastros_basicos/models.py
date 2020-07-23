from django.db import models

class Modalidade(models.Model):
	descricao = models.CharField(max_length=50, blank=False, unique=True, \
		verbose_name='Descrição')

	class Meta:
		verbose_name='Modalidade'
		verbose_name_plural='Modalidades'

	def __str__(self):
		return self.descricao


class Periodicidade(models.Model):
	descricao = models.CharField(max_length=30, blank=False, unique=True, \
		verbose_name='Periodicidade por semana')

	class Meta:
		verbose_name='Período'
		verbose_name_plural='Períodos'

	def __str__(self):
		return self.descricao


class Promocao(models.Model):
	descricao = models.CharField(max_length=30, blank=False, unique=True, \
		verbose_name='Valor promocional')

	class Meta:
		verbose_name='Promoção'
		verbose_name_plural='Promoções'

	def __str__(self):
		return self.descricao


class OfertaDeTurma(models.Model):
	modalidade = models.ForeignKey(Modalidade, related_name='ofertas_da_modalidade')
	periodicidade = models.ForeignKey(Periodicidade, verbose_name='Vezes por semana')
	promocao = models.ForeignKey(Promocao, verbose_name='Tipo de promoção')
	valor_da_mensalidade = models.DecimalField(max_digits=6, decimal_places=2, \
		default=0, verbose_name='Valor da mensalidade')

	class Meta:
		verbose_name='Valor da Mensalidade'
		verbose_name_plural='Valores das Mensalidades'

	def __str__(self):
		return '%s - %s' % (self.modalidade.descricao, self.periodicidade.descricao)

	
class Professor(models.Model):
	SEXO_CHOICES = (
		('M', 'Masculino'),
		('F', 'Feminino'),
	)
	nome = models.CharField(max_length=50, blank=False, unique=True)
	sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)

	class Meta:
		verbose_name='Professor'
		verbose_name_plural='Professores'

	def __str__(self):
		return self.nome


class Turma(models.Model):
	TIPO_TURMA_CHOICES = (
		(1, 'misto'),
		(2, 'feminino'),
		(3, 'kids'),
	)
	DIAS_DE_AULA_CHOICES = (
		(1, '2ª, 4ª e 6ª feira'),
		(2, '3ª e 5ª feira'),
	)
	horario = models.TimeField(null=True, blank=True)
	modalidade = models.ForeignKey(Modalidade, null=True, on_delete=models.CASCADE, \
		related_name='turmas_da_modalidade')
	tipo_turma = models.PositiveSmallIntegerField(choices=TIPO_TURMA_CHOICES, default=1)
	professor = models.ForeignKey(Professor, null=True, on_delete=models.SET_NULL, \
		related_name='turmas_do_professor')
	dias_de_aula = models.PositiveSmallIntegerField(choices=DIAS_DE_AULA_CHOICES, default=1)
	
	class Meta:
		verbose_name='Turma'
		verbose_name_plural='Turmas'

	def get_str_com_valores_de_referencia(self):
		str_oferta = ''
		ofertas = self.modalidade.ofertas_da_modalidade.all().distinct()
		for oferta in ofertas:
			str_oferta = str_oferta + oferta.promocao.descricao.lower() + ' ' \
			+ oferta.periodicidade.descricao.lower() + ' - ' + str(oferta.valor_da_mensalidade) \
			+ '; '
		str_oferta = str_oferta.strip('; ')
		return '%s %s === (valores sugeridos: %s)' % (self.modalidade.descricao, \
			self.horario, str_oferta)

	def __str__(self):
		return '%s - %s - %s' % (self.modalidade.descricao, self.DIAS_DE_AULA_CHOICES[self.dias_de_aula-1][1], self.horario)
		#return self.get_str_com_valores_de_referencia()
