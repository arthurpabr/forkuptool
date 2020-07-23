from django.db import models
from django.db.models.signals import post_save
from django.db.models import Sum
from django.dispatch.dispatcher import receiver
from django.shortcuts import render
from datetime import date
from collections import OrderedDict
from alunos.models import Matricula

class Mensalidade(models.Model):
	SITUACAO_PENDENTE = 1
	SITUACAO_CANCELADA = 2
	SITUACAO_PAGA = 3

	MES_REFERENCIA_CHOICES = (
		(1, 'Janeiro'),
		(2, 'Fevereiro'),
		(3, 'Março'),
		(4, 'Abril'),
		(5, 'Maio'),
		(6, 'Junho'),
		(7, 'Julho'),
		(8, 'Agosto'),
		(9, 'Setembro'),
		(10, 'Outubro'),
		(11, 'Novembro'),
		(12, 'Dezembro'),
	)
	SITUACAO_CHOICES = (
		(SITUACAO_PENDENTE, 'Pendente'),
		(SITUACAO_CANCELADA, 'Cancelada'),
		(SITUACAO_PAGA, 'Paga'),
	)
	matricula = models.ForeignKey(Matricula)
	mes_referencia = models.PositiveSmallIntegerField(choices=MES_REFERENCIA_CHOICES)
	ano_referencia = models.PositiveIntegerField()
	situacao = models.PositiveSmallIntegerField(choices=SITUACAO_CHOICES, default=1)
	data_pagamento = models.DateField(null=True)
	valor_cobrado = models.DecimalField(max_digits=6, decimal_places=2, \
		default=0, verbose_name='Valor cobrado')
	valor_pago = models.DecimalField(max_digits=6, decimal_places=2, \
		default=0, verbose_name='Valor pago')

	class Meta:
		verbose_name='Mensalidade'
		verbose_name_plural='Mensalidades'

	def __str__(self):
		return '%s - %s/%s - %s' % (self.matricula.aluno.nome, self.mes_referencia, \
			self.ano_referencia, self.situacao)

	def get_str_mes_ano(self):
		return '%s/%s' % (self.mes_referencia, self.ano_referencia)

	def get_data_limite_para_pagamento_em_dia(self):
		return date(self.ano_referencia, self.mes_referencia, \
			self.matricula.dia_de_vencimento)

	def get_pago_em_dia(self):
		return self.data_pagamento <= self.get_data_limite_para_pagamento_em_dia()


@receiver(post_save, sender=Matricula)
def matriculas_post_save(sender, instance, **kwargs):
	nova_matricula = instance
	# define o mês atual
	hoje = date.today()
	mes_atual = hoje.month
	ano_atual = hoje.year

	# cria variável de retorno
	novas_mensalidades = list()

	# para a matrícula passada como parâmetro:
		# mes_busca = nova_matricula.mes_de_matricula
		# repete: 
			# busca mensalidade para o mes_busca + nova_matricula
				# existe?
					# sim: não faz nada
					# não: cria nova mensalidade para o mes_busca + nova_matricula
						# com situação 'em aberto'
		# enquanto mes_busca < mes_atual
	mes_busca = nova_matricula.data_matricula.month
	ano_busca = nova_matricula.data_matricula.year
	while ano_busca <= ano_atual:
		if ano_busca == ano_atual:
			#print(' anos iguais (busca e atual) %s - %s' % (ano_busca, ano_atual))
			while mes_busca <= mes_atual:
				if not (Mensalidade.objects.filter( matricula=nova_matricula, \
													mes_referencia=mes_busca, \
													ano_referencia=ano_busca).exists()):
					#print('GERA MENSALIDADE mes/ano %s/%s' % (mes_busca, ano_busca))
					novas_mensalidades.append(gerar_mensalidade(nova_matricula, mes_busca, ano_busca)) 
				mes_busca+=1

		else:
			#print(' anos dif. (busca e atual) %s - %s' % (ano_busca, ano_atual))
			while mes_busca <= 12:
				if not (Mensalidade.objects.filter( matricula=nova_matricula, \
													mes_referencia=mes_busca, \
													ano_referencia=ano_busca).exists()):
					#print('GERA MENSALIDADE mes/ano %s/%s' % (mes_busca, ano_busca))
					novas_mensalidades.append(gerar_mensalidade(nova_matricula, mes_busca, ano_busca))
				mes_busca+=1
			else:
				mes_busca = 1

		ano_busca+=1
		#print('\n')

	return novas_mensalidades


def gerar_mensalidade(matricula, mes_referencia, ano_referencia):
	mensalidade = Mensalidade()
	mensalidade.matricula = matricula
	mensalidade.mes_referencia = mes_referencia
	mensalidade.ano_referencia = ano_referencia
	mensalidade.valor_cobrado = matricula.valor_da_mensalidade
	mensalidade.save()
	return mensalidade


def calcular_mensalidades(request):
	# define o mês atual
	hoje = date.today()
	mes_atual = hoje.month
	ano_atual = hoje.year

	# cria variáveis que serão renderizadas no template
	mensagem_retorno = ''
	novas_mensalidades = list()
	quantidade_mensalidades_ja_existentes = 0

	# busca todas as matrículas ativas
	matriculas_ativas = Matricula.objects.filter(situacao_matricula=1) # 1 = ativas
	if matriculas_ativas: 
		mensagem_retorno = 'Gerando mensalidades para matrículas ativas'
		for matricula_ativa in matriculas_ativas:
			# para cada matrícula ativa:
				# mes_busca = matricula_ativa.mes_de_matricula
				# repete: 
					# busca mensalidade para o mes_busca + matricula_ativa
						# existe?
							# sim: não faz nada
							# não: cria nova mensalidade para o mes_busca + matricula_ativa
								# com situação 'em aberto'
				# enquanto mes_busca < mes_atual
			mes_busca = matricula_ativa.data_matricula.month
			ano_busca = matricula_ativa.data_matricula.year
			#print('Matrícula ativa: \n')
			#print(matricula_ativa)
			while ano_busca <= ano_atual:
				if ano_busca == ano_atual:
					#print(' anos iguais (busca e atual) %s - %s' % (ano_busca, ano_atual))
					while mes_busca <= mes_atual:
						if not (Mensalidade.objects.filter( matricula=matricula_ativa, \
															mes_referencia=mes_busca, \
															ano_referencia=ano_busca).exists()):
							#print('GERA MENSALIDADE mes/ano %s/%s' % (mes_busca, ano_busca))
							novas_mensalidades.append(gerar_mensalidade(matricula_ativa, mes_busca, ano_busca)) 
						else:
							#print('Mensalidade mes/ano %s/%s já existe!' % (mes_busca, ano_busca))
							quantidade_mensalidades_ja_existentes+=1
						mes_busca+=1

				else:
					#print(' anos dif. (busca e atual) %s - %s' % (ano_busca, ano_atual))
					while mes_busca <= 12:
						if not (Mensalidade.objects.filter( matricula=matricula_ativa, \
															mes_referencia=mes_busca, \
															ano_referencia=ano_busca).exists()):
							#print('GERA MENSALIDADE mes/ano %s/%s' % (mes_busca, ano_busca))
							novas_mensalidades.append(gerar_mensalidade(matricula_ativa, mes_busca, ano_busca))
						else:
							#print('Mensalidade mes/ano %s/%s já existe!' % (mes_busca, ano_busca))
							quantidade_mensalidades_ja_existentes+=1
						mes_busca+=1
					else:
						mes_busca = 1

				ano_busca+=1
				#print('\n')

			
	else:
		mensagem_retorno = 'Não encontrada nenhuma matrícula ativa no sistema!'

	context = {'mensagem_retorno': mensagem_retorno, 'novas_mensalidades': novas_mensalidades, \
			'quantidade_mensalidades_ja_existentes': quantidade_mensalidades_ja_existentes, }
	return render(request,"calcular_mensalidades.html",context)


def buscar_mensalidades_em_atraso(request):
	# define o mês atual e ano atual
	hoje = date.today()
	mes_atual = hoje.month
	ano_atual = hoje.year
	dia_atual = hoje.day

	mensalidades_temp = list()
	mensalidades_em_atraso = list()
	# faz a consulta
	mensalidades_temp = Mensalidade.objects.filter(situacao=Mensalidade.SITUACAO_PENDENTE) \
												.order_by('matricula__aluno__nome', '-ano_referencia','-mes_referencia')
	for mensalidade in mensalidades_temp:
		if mensalidade.get_data_limite_para_pagamento_em_dia() < hoje:
			mensalidades_em_atraso.append(mensalidade)

	# totaliza o valor em atraso por aluno
	matricula_da_vez = None
	total_em_atraso_da_vez = 0
	total_em_atraso_geral = 0
	total_em_atraso_por_aluno = dict()
	for mensalidade in mensalidades_em_atraso:
		if mensalidade.matricula != matricula_da_vez:
			if matricula_da_vez != None:
				total_em_atraso_por_aluno[matricula_da_vez.aluno.nome] = total_em_atraso_da_vez
			matricula_da_vez = mensalidade.matricula
			total_em_atraso_da_vez = 0
		total_em_atraso_da_vez += mensalidade.valor_cobrado
		total_em_atraso_geral += mensalidade.valor_cobrado
	# total do último aluno
	total_em_atraso_por_aluno[matricula_da_vez.aluno.nome] = total_em_atraso_da_vez

	total_em_atraso_por_aluno = OrderedDict(sorted(total_em_atraso_por_aluno.items(), \
												key=lambda t: t[0], reverse=False))

	# totaliza o valor em atraso por mes/ano
	total_em_atraso_por_mes_ano = dict()
	
	for mensalidade in mensalidades_em_atraso:
		str_mes_referencia = str(mensalidade.mes_referencia)
		if len(str_mes_referencia) == 1:
			str_mes_referencia = '0'+str_mes_referencia
		str_ano_referencia = str(mensalidade.ano_referencia)
		chave = str_ano_referencia+'_'+str_mes_referencia
		if chave not in total_em_atraso_por_mes_ano:
			total_em_atraso_por_mes_ano[chave] = 0
		total_em_atraso_por_mes_ano[chave] += mensalidade.valor_cobrado

	total_em_atraso_por_mes_ano = OrderedDict(sorted(total_em_atraso_por_mes_ano.items(), \
												key=lambda t: t[0], reverse=True))

	mensagem_retorno = ''
	mensagem_retorno_2 = ''
	if mensalidades_em_atraso:
		mensagem_retorno = 'Existem '+str(len(mensalidades_em_atraso))+' mensalidades em atraso!'
		mensagem_retorno_2 = '(mensalidades c/ vcto anterior ao dia %s)' % (dia_atual)
	else:
		mensagem_retorno = 'Não encontrada nenhuma mensalidade em atraso!'

	context = {'mensagem_retorno': mensagem_retorno, 'mensagem_retorno_2': mensagem_retorno_2,\
			'mensalidades_em_atraso': mensalidades_em_atraso, 'total_em_atraso_por_aluno': \
			total_em_atraso_por_aluno, 'total_em_atraso_geral': total_em_atraso_geral, \
			'total_em_atraso_por_mes_ano': total_em_atraso_por_mes_ano, }

	return render(request,"mensalidades_em_atraso.html",context)


def buscar_mensalidades_recebidas(request):
	# define o número de meses retroativos que se deve buscar mensalidades recebidas
	NUMERO_MESES_AVALIADOS = 6

	# define o mês atual e ano atual
	hoje = date.today()
	mes_atual = hoje.month
	ano_atual = hoje.year

	data_analise_inicial = None # deve ser o primeiro dia do (mês passado - Nº MESES ANÁLISE)
	data_analise_final = None # deve ser o último dia do mês passado

	#mes_analise_final = mes_atual - 1
	mes_analise_final = mes_atual
	ano_analise_final = ano_atual
	if mes_analise_final == 0:
		mes_analise_final = 12
		ano_analise_final -= 1

	mes_analise_inicial = mes_analise_final - NUMERO_MESES_AVALIADOS
	ano_analise_inicial = ano_analise_final
	if mes_analise_inicial <= 0:
		mes_analise_inicial = mes_analise_inicial + 12
		ano_analise_inicial -= 1

	data_analise_inicial = date(ano_analise_inicial,mes_analise_inicial,1)

	dia_analise_final = 31
	if mes_analise_final == 2:
		dia_analise_final = 28
	elif mes_analise_final in (4,6,9,11):
		dia_analise_final = 30

	data_analise_final = date(ano_analise_final,mes_analise_final,dia_analise_final)

	mensalidades_recebidas_ultimos_meses = list()
	mensalidades_recebidas_neste_mes = list()
	mensalidades_a_receber_neste_mes = list()

	numero_de_mensalidades_recebidas_ultimos_meses = 0
	numero_de_mensalidades_recebidas_neste_mes = 0
	numero_de_mensalidades_a_receber_neste_mes = 0

	# faz as consultas
	mensalidades_recebidas_neste_mes = Mensalidade.objects.filter(situacao=Mensalidade.SITUACAO_PAGA, \
		data_pagamento__gte=(date(ano_atual,mes_atual,1))).order_by('-ano_referencia','-mes_referencia')

	mensalidades_a_receber_neste_mes = Mensalidade.objects.filter(situacao=Mensalidade.SITUACAO_PENDENTE, \
		ano_referencia=ano_atual,mes_referencia=mes_atual).order_by('-ano_referencia','-mes_referencia')

	mensalidades_recebidas_ultimos_meses = Mensalidade.objects.filter(situacao=Mensalidade.SITUACAO_PAGA, \
		data_pagamento__range=([data_analise_inicial, data_analise_final])).order_by('-ano_referencia','-mes_referencia')

	mensagem_retorno = ''
	mensagem_retorno_2 = ''
	total_recebido_neste_mes = 0
	total_a_receber_neste_mes = 0
	total_recebido_por_mes_ano = list()

	if mensalidades_a_receber_neste_mes:
		numero_de_mensalidades_a_receber_neste_mes = len(mensalidades_a_receber_neste_mes)
		for mensalidade in mensalidades_a_receber_neste_mes:
			total_a_receber_neste_mes += mensalidade.valor_cobrado

	if mensalidades_recebidas_neste_mes:
		numero_de_mensalidades_recebidas_neste_mes = len(mensalidades_recebidas_neste_mes)
		for mensalidade in mensalidades_recebidas_neste_mes:
			total_recebido_neste_mes += mensalidade.valor_pago

	if mensalidades_recebidas_ultimos_meses:
		numero_de_mensalidades_recebidas_ultimos_meses = len(mensalidades_recebidas_ultimos_meses)
		primeira_mensalidade = mensalidades_recebidas_ultimos_meses[0]
		str_mes_para_comparacao = str(primeira_mensalidade.mes_referencia)
		str_ano_para_comparacao = str(primeira_mensalidade.ano_referencia)
		if len(str_mes_para_comparacao) == 1:
			str_mes_para_comparacao = '0'+str_mes_para_comparacao

		valor_do_mes_da_vez = 0
		valor_de_meses_anteriores_da_vez = 0
		total_mes = 0
		total_meses_anteriores = 0

		for mensalidade in mensalidades_recebidas_ultimos_meses:
		
			str_mes_da_vez = str(mensalidade.mes_referencia)
			str_ano_da_vez = str(mensalidade.ano_referencia)
		
			if len(str_mes_da_vez) == 1:
				str_mes_da_vez = '0'+str_mes_da_vez

			if str_mes_da_vez != str_mes_para_comparacao:
				chave = str_ano_para_comparacao+'_'+str_mes_para_comparacao
				total_recebido_por_mes_ano.append({'ano_mes': chave,\
					'valor_do_mes': valor_do_mes_da_vez, \
					'valor_de_meses_anteriores': valor_de_meses_anteriores_da_vez ,\
					'valor_total_do_mes': (valor_do_mes_da_vez+valor_de_meses_anteriores_da_vez)})
				valor_do_mes_da_vez = 0
				valor_de_meses_anteriores_da_vez = 0
				str_mes_para_comparacao = str_mes_da_vez

			if mensalidade.get_pago_em_dia():
				valor_do_mes_da_vez += mensalidade.valor_pago
				total_mes += mensalidade.valor_pago
			else:
				valor_de_meses_anteriores_da_vez += mensalidade.valor_pago
				total_meses_anteriores += mensalidade.valor_pago

		# acumula valores da última mensalidade
		chave = str_ano_para_comparacao+'_'+str_mes_para_comparacao
		total_recebido_por_mes_ano.append({'ano_mes': chave,\
			'valor_do_mes': valor_do_mes_da_vez, \
			'valor_de_meses_anteriores': valor_de_meses_anteriores_da_vez ,\
			'valor_total_do_mes': (valor_do_mes_da_vez+valor_de_meses_anteriores_da_vez)})

		# gera um totalizador
		chave = 'Total'
		total_recebido_por_mes_ano.append({'ano_mes': chave,\
			'valor_do_mes': total_mes, \
			'valor_de_meses_anteriores': total_meses_anteriores ,\
			'valor_total_do_mes': (total_mes+total_meses_anteriores)})

	if mensalidades_recebidas_ultimos_meses:
		mensagem_retorno = str(len(mensalidades_recebidas_ultimos_meses))+ \
			' mensalidades recebidas'
		mensagem_retorno_2 = '(nos últimos '+str(NUMERO_MESES_AVALIADOS)+' meses, incluindo mês atual)'
	else:
		mensagem_retorno = 'Não encontrada nenhuma mensalidade recebida nos últimos '+ \
		str(NUMERO_MESES_AVALIADOS)+' meses!'

	context = {'mensagem_retorno': mensagem_retorno, 'mensagem_retorno_2': mensagem_retorno_2, \
		'total_recebido_por_mes_ano': total_recebido_por_mes_ano, 'total_a_receber_neste_mes': \
		total_a_receber_neste_mes, 'total_recebido_neste_mes': total_recebido_neste_mes, \
		'numero_de_mensalidades_recebidas_ultimos_meses': numero_de_mensalidades_recebidas_ultimos_meses,
		'numero_de_mensalidades_recebidas_neste_mes': numero_de_mensalidades_recebidas_neste_mes,
		'numero_de_mensalidades_a_receber_neste_mes': numero_de_mensalidades_a_receber_neste_mes, }

	return render(request,"mensalidades_recebidas.html",context)
	