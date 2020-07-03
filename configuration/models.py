from django.db import models

# ordenar dicionários
from operator import itemgetter

# para saber se um arquivo é binário ou não
from binaryornot.check import is_binary 


class ThreadTask(models.Model):
    task = models.CharField(max_length=30, blank=True, null=True)
    is_done = models.BooleanField(blank=False,default=False)



class ConfiguracaoGeral(models.Model):
	descricao = models.CharField(u'Descrição', null=False, blank=False, unique=True, max_length=150)
	descricao_vendor = models.CharField(u'Descrição do repositório fornecedor', null=False, blank=False, max_length=150, default='')
	descricao_client = models.CharField(u'Descrição do repositório cliente', null=False, blank=False, max_length=150, default='')
	path_repositorio_vendor = models.CharField(u'Caminho completo do repositório fornecedor', null=False, blank=False, max_length=150)
	path_repositorio_client = models.CharField(u'Caminho completo do repositório cliente', null=False, blank=False, max_length=150)

	class Meta:
		verbose_name = u'Configuração geral do projeto'
		verbose_name_plural = u'Configurações gerais do projeto'

	def __str__(self):
		return ('id {} - {}').format(self.pk, self.descricao)



class Comparacao(models.Model):
	datahorario_execucao = models.DateTimeField(auto_now=True, verbose_name=u'Data/Horário de execução')
	descricao_vendor = models.CharField(u'Obs. repositório fornecedor', null=False, blank=False, max_length=150, default='')
	descricao_client = models.CharField(u'Obs. repositório cliente', null=False, blank=False, max_length=150, default='')
	path_repositorio_vendor = models.CharField(u'Repositório fornecedor', null=False, blank=False, max_length=150)
	path_repositorio_client = models.CharField(u'Repositório cliente', null=False, blank=False, max_length=150)
	numero_arquivos_ignorados = models.IntegerField(u'Nº de arquivos ignorados por regra de negócio', null=False, default=0)

	class Meta:
		verbose_name = u'Comparação entre repositórios'
		verbose_name_plural = u'Comparações entre repositórios'


	def __str__(self):
		return ('id {} - {}').format(self.pk, self.datahorario_execucao.strftime('%d/%m/%Y %H:%M:%S'))


	def get_arquivos_comparados(self, somente_vendor = False, somente_diferentes = False):
		qs = ArquivosComparados.objects.filter(comparacao=self).order_by('arquivo_vendor__caminho_completo')

		if somente_vendor:
			qs = qs.filter(arquivo_vendor__tem_no_client = False)

		if somente_diferentes:
			qs = qs.filter(arquivo_vendor__igual_ao_client = False)
		return qs


	def get_agrupados_por_tipo(self, somente_diferentes = False):
		arquivos_comparados = self.get_arquivos_comparados(somente_diferentes=somente_diferentes)
		# percorre a lista obtendo totais por tipo
		tipos_de_arquivos_identificados = dict()
		tipos_de_arquivos_identificados['nao_determinada'] = 0
		for dupla in arquivos_comparados:
			extensao_tipo = dupla.arquivo_vendor.extensao_tipo
			if extensao_tipo:
				if extensao_tipo in tipos_de_arquivos_identificados:
					tipos_de_arquivos_identificados[extensao_tipo] +=1
				else:
					tipos_de_arquivos_identificados[extensao_tipo] = 1
			else:
				# por algum motivo a extensão do arquivo vendor não pode ser determinada
				tipos_de_arquivos_identificados['nao_determinada'] += 1

		# ordena o dicionário de tipos de arquivos, com base na quantidade
		# obs.: o resultado da ordenação deixa de ser um dicionário e vira uma lista
		tipos_de_arquivos_identificados = sorted(tipos_de_arquivos_identificados.items(), key=itemgetter(1), reverse=True)

		return {'tipos_de_arquivos_identificados': tipos_de_arquivos_identificados, 'total': len(arquivos_comparados)}


	def get_agrupados_por_modulo(self, somente_diferentes = False):
		arquivos_comparados = self.get_arquivos_comparados(somente_diferentes=somente_diferentes)
		# percorre a lista obtendo totais por modulo
		modulos_identificados = dict()
		modulos_identificados['nao_determinado'] = 0
		for dupla in arquivos_comparados:
			modulo = dupla.arquivo_vendor.modulo
			if modulo:
				if modulo in modulos_identificados:
					modulos_identificados[modulo] +=1
				else:
					modulos_identificados[modulo] = 1
			else:
				# por algum motivo a extensão do arquivo vendor não pode ser determinada
				modulos_identificados['nao_determinado'] += 1

		# ordena o dicionário de tipos de arquivos, com base na quantidade
		# obs.: o resultado da ordenação deixa de ser um dicionário e vira uma lista
		modulos_identificados = sorted(modulos_identificados.items(), key=itemgetter(1), reverse=True)
		return {'modulos_identificados': modulos_identificados, 'total': len(arquivos_comparados)}


	def get_agrupados_por_modulo_e_tipo(self, somente_diferentes = False, somar_linhas_incluidas_excluidas = False,\
		considerar_percentual_total_linhas_do_arquivo = False):

		arquivos_comparados = self.get_arquivos_comparados(somente_diferentes=somente_diferentes)
		
		# as duas listas abaixo são criadas somente para facilitar análises posteriores do controller que utilizar este método
		descricao_modulos = list()
		descricao_tipos = list()

		modulos_e_tipos_identificados = dict()
		modulos_e_tipos_identificados['nao_determinado'] = dict()
		modulos_e_tipos_identificados['nao_determinado']['nao_determinado'] = 0

		# percorre a lista obtendo totais por modulo e tipo
		for dupla in arquivos_comparados:

			# # CONTAR NÚMERO DE LINHAS DO ARQUIVO - trecho provisório
			# try:
			# 	arquivo = open(self.path_repositorio_vendor+dupla.arquivo_vendor.caminho_completo, 'r')
			# 	linhas = arquivo.readlines()
			# 	numero_linhas_total = len(linhas)
			# 	arquivo.close()
			# except Exception as e:
			# 	numero_linhas_total = 0

			if somar_linhas_incluidas_excluidas:
				incremento = dupla.numero_linhas_inseridas+dupla.numero_linhas_excluidas
			else:
				incremento = 1

			modulo = dupla.arquivo_vendor.modulo
			extensao_tipo = dupla.arquivo_vendor.extensao_tipo

			if modulo not in descricao_modulos:
				descricao_modulos.append(modulo)

			if extensao_tipo not in descricao_tipos:
				descricao_tipos.append(extensao_tipo)

			if modulo:
				if modulo in modulos_e_tipos_identificados:
					if extensao_tipo:
						if extensao_tipo in modulos_e_tipos_identificados[modulo]:
							modulos_e_tipos_identificados[modulo][extensao_tipo] +=incremento
						else:
							modulos_e_tipos_identificados[modulo][extensao_tipo] = incremento

					else: # extensão não identificada
						modulos_e_tipos_identificados[modulo]['nao_determinado'] +=incremento
				else:
					modulos_e_tipos_identificados[modulo] = dict()
					if extensao_tipo:
						modulos_e_tipos_identificados[modulo][extensao_tipo] = incremento

					else: # extensão não identificada
						modulos_e_tipos_identificados[modulo]['nao_determinado'] = incremento
			
			else: # módulo não identificado
				if extensao_tipo:
					if extensao_tipo in modulos_e_tipos_identificados['nao_determinado']:
						modulos_e_tipos_identificados['nao_determinado'][extensao_tipo] +=incremento
					else:
						modulos_e_tipos_identificados['nao_determinado'][extensao_tipo] = incremento

				else: # módulo e extensão não identificados
					modulos_e_tipos_identificados['nao_determinado']['nao_determinado'] +=incremento

		# converte os valores apurados em % pelo número de linhas do arquivo, se for o caso


		return {'modulos_e_tipos_identificados': modulos_e_tipos_identificados, 'descricao_modulos': descricao_modulos, 'descricao_tipos': descricao_tipos}



	def get_agrupados_por_commit(self, somente_diferentes = True):
		arquivos_comparados = self.get_arquivos_comparados(somente_diferentes=somente_diferentes)
		# percorre a lista obtendo totais por commit
		commits_identificados_dict = dict()
		commits_identificados_list = list()
		for dupla in arquivos_comparados:
			commits_em_client_que_nao_estao_em_vendor = dupla.get_commits_em_client_que_nao_estao_em_vendor()

			if commits_em_client_que_nao_estao_em_vendor:
				for c in commits_em_client_que_nao_estao_em_vendor:
					if c not in commits_identificados_list:
						commits_identificados_list.append(c)
						commits_identificados_dict[c] = 1
					else:
						commits_identificados_dict[c] += 1

		# ordena o dicionário de commits, com base na quantidade
		# obs.: o resultado da ordenação deixa de ser um dicionário e vira uma lista
		commits_identificados_dict = sorted(commits_identificados_dict.items(), key=itemgetter(1), reverse=True)
		return {'commits_identificados': commits_identificados_dict, 'total': len(arquivos_comparados)}		



class Commit(models.Model):
	string_hash = models.CharField(u'String SHA do commit', null=False, blank=False, max_length=50, unique=True, primary_key=True)

	def __str__(self):
		return ('{}').format(self.string_hash)



class Arquivo(models.Model):
	nome = models.CharField(u'Nome do arquivo', null=False, blank=False, max_length=150)
	caminho_completo = models.CharField(u'Caminho completo do arquivo', null=False, blank=False, max_length=250)
	extensao_tipo = models.CharField(u'Extensão / tipo do arquivo', null=False, blank=False, max_length=30)

	def __str__(self):
		return ('{}').format(self.caminho_completo)

	# exemplo de método de classe
	@staticmethod
	def obter_apenas_nome(string):
		list_str = string.split('/')
		return (list_str[len(list_str)-1])

	# exemplo de método de classe
	@staticmethod
	def obter_extensao_tipo(string):
		list_str = string.split('.')
		return (list_str[len(list_str)-1])

	# exemplo de método de classe
	@staticmethod
	def deve_ser_ignorado(string):
		NOMES_ARQUIVOS_IGNORADOS = ['.gitignore','.gitlab-ci.yml','Dockerfile','Dockerfile.base','Dockerfile.ci',]
		NOMES_DIRETORIOS_IGNORADOS = ['migrations','features',]

		list_str = string.split('/')
		file_name = list_str[len(list_str)-1]
		file_dir = list_str[len(list_str)-2]
		if file_name in NOMES_ARQUIVOS_IGNORADOS or file_dir in NOMES_DIRETORIOS_IGNORADOS:
			return True

		return False

	# exemplo de atributo calculado
	@property
	def modulo(self):
		list_str = self.caminho_completo.split('/')
		return (list_str[0])

	# exemplo de atributo calculado
	@property
	def extensao_tipo(self):
		return Arquivo.obter_extensao_tipo(self.nome)


	def get_commits_do_arquivo(self):
		return self.commits.all()



class ArquivoVendor(Arquivo):
	tem_no_client = models.BooleanField(u'Tem correspondente no client?', default=True)
	igual_ao_client = models.BooleanField(u'É igual ao correspondente no client?', default=True)
	commits = models.ManyToManyField('Commit', verbose_name=u'Commits que afetaram o arquivo')



class ArquivoClient(Arquivo):
	tem_no_vendor = models.BooleanField(u'Tem correspondente no vendor?', default=True)
	igual_ao_vendor = models.BooleanField(u'É igual ao correspondente no vendor?', default=True)
	commits = models.ManyToManyField('Commit', verbose_name=u'Commits que afetaram o arquivo')



class ArquivosComparados(models.Model):
	comparacao = models.ForeignKey('Comparacao', verbose_name=u'Execução de comparação entre repositórios',on_delete=models.CASCADE)
	arquivo_vendor = models.ForeignKey('ArquivoVendor', verbose_name=u'Arquivo vendor',on_delete=models.CASCADE, blank=True, null=True)
	arquivo_client = models.ForeignKey('ArquivoClient', verbose_name=u'Arquivo client',on_delete=models.CASCADE, blank=True, null=True)
	numero_linhas_inseridas = models.IntegerField(u'Nº linhas inseridas', null=False, default=0)
	numero_linhas_excluidas = models.IntegerField(u'Nº linhas excluídas', null=False, default=0)
	analise_diff_realizada = models.BooleanField(u'Foi realizada análise de diff entre os arquivos?', default=False)
	analise_diff = models.TextField(u'Análise de diff entre os arquivos', default='')

	class Meta:
		verbose_name = u'Arquivos comparados'
		verbose_name_plural = u'Arquivos comparados'

	def __str__(self):
		return ('{}').format(self.arquivo_vendor.caminho_completo)


	""" 
	Vendor e client são, em tese, do mesmo tipo/extensão. Portanto, para saber se são binários ou não 
	bastar testar apenas um dos dois.
	"""
	def eh_binario(self):
		return is_binary(self.comparacao.path_repositorio_vendor+self.arquivo_vendor.caminho_completo)


	def get_commits_em_client_que_nao_estao_em_vendor(self):
		if not self.arquivo_client:
			return None

		if not self.arquivo_vendor.tem_no_client:
			return None

		if self.arquivo_vendor.igual_ao_client:
			return None

		lista_de_commits = list()
		commits_em_vendor = self.arquivo_vendor.get_commits_do_arquivo()
		commits_em_client = self.arquivo_client.get_commits_do_arquivo()
		for c in commits_em_client:
			if c not in commits_em_vendor:
				lista_de_commits.append(c)
		return lista_de_commits



class ConfiguracaoFerramenta(models.Model):
	description = models.CharField(u'Descrição geral da configuração', null=False, blank=False, unique=True, max_length=150)

	alias_project = models.CharField(u'Alias do projeto de software a ser customizado', null=False, blank=False, max_length=150, default='')
	alias_vendor = models.CharField(u'Alias do projeto original', null=False, blank=False, max_length=150, default='')
	alias_client = models.CharField(u'Alias do projeto customizado', null=False, blank=False, max_length=150, default='')
	
	branch_vendor = models.CharField(u'Branch do projeto original', null=False, blank=False, max_length=150, default='')
	branch_auxilary_files = models.CharField(u'Branch dos arquivos auxiliares', null=False, blank=False, max_length=150, default='')

	path_vendor = models.CharField(u'Caminho completo do projeto original', null=False, blank=False, max_length=150)
	path_auxiliary_files = models.CharField(u'Caminho completo dos arquivos auxiliares', null=False, blank=False, max_length=150)
	path_patch_files = models.CharField(u'Caminho completo dos arquivos de patch', null=False, blank=False, max_length=150)

	class Meta:
		verbose_name = u'Configuração de execução da ferramenta'
		verbose_name_plural = u'Configurações de execução da ferramenta'

	def __str__(self):
		return ('id {} - {}').format(self.pk, self.description)


