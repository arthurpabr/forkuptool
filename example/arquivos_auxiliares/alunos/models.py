from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from cadastros_basicos.models import Turma, Promocao, Recepcionista


class Matricula(models.Model):
	SITUACAO_MATRICULA_CHOICES = (
		(1, 'Ativa'),
		(2, 'Suspensa'),
	)
	aluno = models.ForeignKey(Aluno)
	turma = models.ForeignKey(Turma)
	recepcionista = models.ForeignKey(Recepcionista, \
		verbose_name='Recepcionista responsável', blank=False, null=True, default=None)
	quantas_modalidades = models.ForeignKey(Promocao, verbose_name='Quantas modalidades o aluno vai fazer?', \
		blank=False, default=1)
	valor_da_mensalidade = models.DecimalField(max_digits=6, decimal_places=2, \
		verbose_name='Valor mensalidade do aluno', blank=False)
	dia_de_vencimento = models.IntegerField(null=False, blank=False, default=10, \
		validators=[MinValueValidator(1), MaxValueValidator(28)])
	data_matricula = models.DateField(null=False, blank=False)
	situacao_matricula = models.PositiveSmallIntegerField(choices=SITUACAO_MATRICULA_CHOICES, \
		default=1)

	class Meta:
		verbose_name='Matrícula'
		verbose_name_plural='Matrículas'

	def __str__(self):
		return '%s - %s %s ' % (self.aluno.nome, self.turma.modalidade, self.turma.horario)