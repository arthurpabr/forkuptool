from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from cadastros_basicos.models import Turma, Promocao

class Aluno(models.Model):
	SEXO_CHOICES = (
		('M', 'Masculino'),
		('F', 'Feminino'),
	)
	nome = models.CharField(max_length=100, blank=False)
	sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
	data_nascimento = models.DateField()
	rg = models.CharField(max_length=20, null=True, blank=True, verbose_name='RG')
	cpf = models.CharField(max_length=20, null=True, blank=True, verbose_name='CPF')
	email = models.EmailField(null=True, blank=True)
	numero_celular = models.CharField(max_length=30, verbose_name='Celular')
	numero_fixo = models.CharField(max_length=30, verbose_name='Fixo')
	endereco_completo = models.CharField(max_length=150, null=True, blank=True, \
		verbose_name='Endereço completo')
	nome_do_responsavel = models.CharField(max_length=100, null=True, blank=True)
	contato_do_responsavel = models.CharField(max_length=100, null=True, blank=True)

	class Meta:
		verbose_name='Aluno(a)'
		verbose_name_plural='Alunos(as)'

	def __str__(self):
		return self.nome


class Matricula(models.Model):
	SITUACAO_MATRICULA_CHOICES = (
		(1, 'Ativa'),
		(2, 'Suspensa'),
	)
	aluno = models.ForeignKey(Aluno)
	turma = models.ForeignKey(Turma)
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