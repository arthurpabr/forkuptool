import json
import threading
import os
import filecmp

from django.shortcuts import render, redirect
from django.http import JsonResponse

from pydriller import RepositoryMining, GitRepository
from datetime import datetime
from binaryornot.check import is_binary 

from .forms import AnalisarTimelineForm, CompararRepositoriosForm, \
	VisualizarComparacaoRepositoriosForm

from configuration.models import ConfiguracaoGeral, ConfiguracaoFerramenta, \
	ThreadTask, Comparacao, ArquivoVendor, ArquivoClient, ArquivosComparados, \
	Commit

from forkuptool.settings import LENGTH_INFO_CLIENT

from .utils import identificar_arquivos_em_conflito, \
	contar_ocorrencias_desta_linha_neste_arquivo, \
	contar_linhas_entre_esses_linhas_neste_arquivo, \
	buscar_detalhes_diff_entre_arquivos, check_thread_task

from .util import diff2HtmlCompare


def index(request):
    return render(request, 'analyze.html', {'title': 'Forkuptool',
    	'subtitle': 'Módulo de análise de repositórios', 'messages': None, })



def info_criacao_client(request):

	# busca a configuração para o SUAP
	config = ConfiguracaoFerramenta.objects.get(id=2) 
	repo_vendor = GitRepository(config.path_vendor)
	repo_client = GitRepository(config.path_auxiliary_files)
	commits_vendor = repo_vendor.get_list_commits()
	list_hash_vendor = []
	for c in commits_vendor:
	    list_hash_vendor.append(c.hash)
	commits_client = repo_client.get_list_commits()
	list_hash_client = []
	for c in commits_client:
	    list_hash_client.append(c.hash)
	hash_n_primeiros_commits_somente_client = []
	n_primeiros_commits_somente_client = []
	for c in list_hash_client:
	    if c not in list_hash_vendor: 
	        hash_n_primeiros_commits_somente_client.append(c)
	        if len(hash_n_primeiros_commits_somente_client) == LENGTH_INFO_CLIENT:
	            break
	
	for h in hash_n_primeiros_commits_somente_client:
		commit_da_vez = repo_client.get_commit(h)
		candidato_merge_vendor = False
		if commit_da_vez.merge:
			tem_pai_vendor = False
			tmp_parents = commit_da_vez.parents
			for p in tmp_parents:
				if p in list_hash_vendor:
					tem_pai_vendor = True
			if tem_pai_vendor:
				candidato_merge_vendor = True

		info = {'author_date': commit_da_vez.author_date,\
				'hash': commit_da_vez.hash,\
				'parents': commit_da_vez.parents,\
				'author_name': commit_da_vez.author.name,\
				'merge': commit_da_vez.merge,\
				'candidato_merge_vendor': candidato_merge_vendor,\
				'msg': commit_da_vez.msg}
		n_primeiros_commits_somente_client.append(info)
		commit_da_vez = None
		info = None

	for c in n_primeiros_commits_somente_client:
	    print(('{} ({}) - {} - {} - {}').format(c['author_date'], c['hash'][0:7], c['author_name'], c['merge'], c['msg'][0:80]))

	title = 'Forkuptool'
	subtitle = 'Informações de criação repositório client'	
	return render(request, 'info_criacao_client.html', locals())



def analisar_timeline(request):

	# se POST será necessário processar os dados do formulário
	if request.method == 'POST':
		form = AnalisarTimelineForm(request.POST)
		if form.is_valid():

			data_inicial = datetime.strptime(request.POST['data_inicial']+' 00:00:00', "%d/%m/%Y %H:%M:%S")
			data_final = datetime.strptime(request.POST['data_final']+' 23:59:59', "%d/%m/%Y %H:%M:%S")
			if 'resumida' not in request.POST:
				resumida = False
			else:
				resumida = request.POST['resumida']

			config = ConfiguracaoFerramenta.objects.get(id=2) 
			url = [] 
			commits_vendor = [] 
			commits_vendor_hash = [] 
			commits_aux = [] 
			commits_aux_hash = [] 
			url.append(config.path_vendor) 
			url.append(config.path_auxiliary_files) 

			contador_commits_aux_nao_vendor_sim_geral = 0
			contador_commits_aux_sim_vendor_nao_geral = 0
			contador_commits_aux_sim_vendor_nao_tipo_merge = 0

			primeiro_commit_geral = None
			ultimo_commit_geral = None
			ultimo_commit_client = None

			# percorre uma vez para povoar os vetores de hash
			contador = 0 
			commits = RepositoryMining(url[0], since=data_inicial, to=data_final).traverse_commits() 
			for commit in commits: 
				commits_vendor_hash.append(commit.hash) 
				contador += 1

			commits = RepositoryMining(url[1], since=data_inicial, to=data_final).traverse_commits()
			for commit in commits:
				commits_aux_hash.append(commit.hash) 
				contador += 1

			# percorre uma segunda vez povoando os vetores de dados
			contador = 0 
			commits = RepositoryMining(url[0], since=data_inicial, to=data_final).traverse_commits() 
			for commit in commits:
				if not primeiro_commit_geral:
					primeiro_commit_geral = commit
				if not ultimo_commit_geral:
					ultimo_commit_geral = commit
				if commit.committer_date > ultimo_commit_geral.committer_date:
					ultimo_commit_geral = commit
				if commit.hash not in commits_aux_hash:
					contador_commits_aux_nao_vendor_sim_geral += 1
					dados = {'id': contador, 'content': commit.hash[0:7],\
								'group': 0, 'start': str(commit.committer_date),\
								'className': 'green', 'title': commit.msg}
				else:
					dados = {'id': contador, 'content': commit.hash[0:7],\
								'group': 0, 'start': str(commit.committer_date),\
								'title': commit.msg}

				commits_vendor.append(dados) 
				contador += 1

			commits = RepositoryMining(url[1], since=data_inicial, to=data_final).traverse_commits() 
			for commit in commits:  
				if commit.hash not in commits_vendor_hash:
					if not ultimo_commit_client:
						ultimo_commit_client = commit
					if commit.committer_date > ultimo_commit_client.committer_date:
						ultimo_commit_client = commit
					contador_commits_aux_sim_vendor_nao_geral += 1
					if commit.merge:
						contador_commits_aux_sim_vendor_nao_tipo_merge += 1
						dados = {'id': contador,\
							'content': '('+str(contador_commits_aux_sim_vendor_nao_geral)+') '+commit.hash[0:7],\
							'group': 1, 'start': str(commit.committer_date),\
							'className': 'blue', 'title': commit.msg}
						
					else:
						dados = {'id': contador,\
							'content': '('+str(contador_commits_aux_sim_vendor_nao_geral)+') '+commit.hash[0:7],\
							'group': 1, 'start': str(commit.committer_date),\
							'className': 'red', 'title': commit.msg}
				else:
					dados = {'id': contador, 'content': commit.hash[0:7],\
								'group': 1, 'start': str(commit.committer_date),\
								'title': commit.msg}

				commits_aux.append(dados) 
				contador += 1

			todos_commits = commits_vendor + commits_aux

			json_geral = json.dumps(todos_commits)
			title = 'Forkuptool'
			return render(request, 'analisar_timeline_show.html', locals())

	# se GET cria o formulário em branco
	form = AnalisarTimelineForm()
	title = 'Forkuptool'
	subtitle = 'Analisar timeline'	
	return render(request, 'analisar_timeline.html', locals())



def simular_conflitos(request):

	config = ConfiguracaoFerramenta.objects.get(id=2) 
	gr = GitRepository(config.path_auxiliary_files)
	# commits_vendor = (
	# 	'fca529f', 'a639855', '168e36a', '48374cd', 'e0428a2', 
	# 	'49275f2', '25ad58d', 'd7c1bdf', '75c8a35', '41f8ace', 
	# 	'69e7a98', 'a8f4829', 'be98898', 'f7e815a', '03f178c', 
	# 	'fc7af49', '74a8748', 'a58320e', '1d4fa85', '855e138', 
	# 	'671aaa8', '06a967e', '048aa85', '9119a3f', 'a74d6ae', 
	# 	'bb83f28', '8f5e756', '83610c5', '5c5fc7d', '5e74902', 
	# 	'ce59547', '923f5ee', 'df8666d', 'c219a97', 'aefcd22', 
	# 	'0be9ee9', 'bb3c479', 'e0557a0', 'f02b0c3', '8d5cdfa', 
	# 	'e944c53', 
	# 	'0a93957',)
	commits_vendor = (
		'48d1edb',)
	
	# commits_client = (
	# 	'a9cb50e', '085aa2a', '66165fd', '6eb4d4c', '353a877', 
	# 	'b1bf9fe', '7891bb7', '70ddc11', '6a858e2', 'bbc8bea', 
	# 	'df85d8e', 'b57eca7', '914f9b1', 'e8faf15', '3a1a355', 
	# 	'da45411', '53464c7', '75f241c', '1e8e20b', '7c9583c',
	#     '7482e54', 'a2c2ae2', 'dc18528', '5b308d9', 'fc62c99', 
	# 	'2977dbf', '90aa392', 'd2c2f36', 'e083730', '2edc4b3', 
	# 	'3328138', '3595f20', 'd6b40e5', '1c82a62', '757c692', 
	# 	'0230fb0', '3094585', '43a6ab3', '151f8a3', 'ec90a78', 
	# 	'5a51d1a', 
	# 	'287f6ed',)
	commits_client = (
		'd472976',)


	contador = 0
	conflitos_por_rodada = dict()
	for c in commits_vendor:
		total_trechos_conflitantes = 0
		total_linhas_conflitantes = 0
		conflitos = dict()

		gr.git().checkout('master')
		gr.git().checkout(c)
		branch_vendor = 't'+str(contador+1)+'vendor'
		gr.git().branch(branch_vendor)
		gr.git().checkout('master')
		gr.checkout(commits_client[contador])
		branch_client = 't'+str(contador+1)+'client'
		gr.git().branch(branch_client)
		branch_merge = 't'+str(contador+1)+'merge'
		gr.git().branch(branch_merge)
		gr.git().checkout(branch_merge)

		try:
			# tenta fazer o merge; se executar sem erros é porque não houve conflito
			gr.git().merge(branch_vendor)
		except Exception as e:
			linhas_com_erro = str(e)
			linhas_com_erro = linhas_com_erro.split('\n')
			arquivos_com_conflito = identificar_arquivos_em_conflito(linhas_com_erro)

			for a in arquivos_com_conflito:
				numero_trechos_conflitantes = 0
				numero_linhas_conflitantes = 0
				caminho_completo = gr.path.as_posix()+'/'+a
				if not is_binary(caminho_completo):
					numero_trechos_conflitantes = contar_ocorrencias_desta_linha_neste_arquivo(
					'<<<<<<< HEAD', caminho_completo)
					numero_linhas_conflitantes = contar_linhas_entre_esses_linhas_neste_arquivo(
					    '<<<<<<< HEAD', '=======', caminho_completo)
				else:
					numero_trechos_conflitantes = 1
					numero_linhas_conflitantes = 1
				total_trechos_conflitantes+=numero_trechos_conflitantes
				total_linhas_conflitantes+=numero_linhas_conflitantes
				conflitos[caminho_completo] = numero_trechos_conflitantes
			gr.git().merge('--abort')
			gr.git().checkout('master')

		print(('Processou par {}: {} - {}').format((contador + 1), c, commits_client[contador]))

		conflitos_por_rodada[(contador + 1)] = (conflitos, total_trechos_conflitantes, total_linhas_conflitantes)
		contador += 1
	
	print(conflitos_por_rodada)
	title = 'Forkuptool'
	subtitle = 'Simulação de conflitos'	
	return render(request, 'simular_conflitos.html', locals())



def comparar_repositorios(request):
	# busca as opções de configuração geral registradas no banco de dados
	configuracaogeral_choices = ConfiguracaoGeral.objects.all()
	configuracaogeral_choices_to_choicefield = list()
	for configuracao in configuracaogeral_choices:
		configuracaogeral_choices_to_choicefield.append([configuracao.pk,configuracao.descricao])

	# se POST será necessário processar os dados do formulário
	if request.method == 'POST':
		task = ThreadTask()
		task.save()
		t = threading.Thread(target=comparar_repositorios_task,args=[task.id, request.POST['configuracaogeral_escolhida']])
		t.setDaemon(True)
		t.start()
		return JsonResponse({'id':task.id})

	# se GET cria o formulário em branco
	else:
		form = CompararRepositoriosForm(configuracaogeral_choices_to_choicefield)
	title = 'Forkuptool'
	subtitle = 'Realizar comparação entre repositórios'
	return render(request, 'comparar_repositorios.html', locals())



def comparar_repositorios_task(task_id, configuracaogeral_escolhida):
	print("Received task", task_id)

	# busca a configuração para o id informado
	configuracaogeral = ConfiguracaoGeral.objects.get(pk=configuracaogeral_escolhida)
	
	# cria registro de Comparacao para esta execução
	comparacao = Comparacao()
	comparacao.descricao_vendor = configuracaogeral.descricao_vendor
	comparacao.descricao_client = configuracaogeral.descricao_client
	comparacao.path_repositorio_vendor = configuracaogeral.path_repositorio_vendor
	comparacao.path_repositorio_client = configuracaogeral.path_repositorio_client
	comparacao.save()

	"""
	Inicia a análise/comparação entre os respositórios, percorrendo o repositório vendor
	- obtém um objeto para iteração sobre o repositório vendor
	- itera sobre o objeto vendor
	- para cada item de vendor:
	"""
	git_vendor = GitRepository(configuracaogeral.path_repositorio_vendor)
	git_client = GitRepository(configuracaogeral.path_repositorio_client)
	files_in_vendor = git_vendor.files()

	# para debug
	#contador_interrupcao = 0

	numero_arquivos_ignorados = 0
	for file_vendor in files_in_vendor:
		#contador_interrupcao += 1
		#if contador_interrupcao > 300:
		#	break

		"""
		- cria um objeto ArquivoVendor
		- cria um objeto ArquivoClient
		- busca informações do arquivo vendor e atualiza atributos correspondentes
			arquivo_vendor.nome
			arquivo_vendor.caminho_completo
			arquivo_vendor.extensao_tipo ==> em 14/05/19: virou atributo calculado (property)
		"""
		arquivo_vendor = ArquivoVendor()
		arquivo_client = ArquivoClient()

		"""
			Em 20/05/2019: verifica se o arquivo deve ou não ser ignorado na análise
		"""
		if ArquivoVendor.deve_ser_ignorado(file_vendor):
			numero_arquivos_ignorados += 1
			continue

		# file_vendor correspondente ao nome completo do arquivo (caminho completo + nome)
		# é necessário guardar o caminho completo do arquivo SOMENTE do projeto, desconsiderando o caminho da máquina local
		arquivo_vendor.nome = ArquivoVendor.obter_apenas_nome(file_vendor)
		arquivo_vendor.caminho_completo = file_vendor.replace(configuracaogeral.path_repositorio_vendor,'')
		#arquivo_vendor.extensao_tipo = ArquivoVendor.obter_extensao_tipo(arquivo_vendor.nome)

		"""
			- verifica se existe correspondente em client
		"""
		if not os.path.isfile(configuracaogeral.path_repositorio_client+arquivo_vendor.caminho_completo):
			"""
				- se não existir: 
					arquivo_vendor.tem_no_client = False
					arquivo_vendor.igual_ao_client = False
					arquivo_client = None
			"""
			arquivo_vendor.tem_no_client = False
			arquivo_vendor.igual_ao_client = False
			arquivo_client = None
		else:
			"""				
			- se existir:
				- busca informações do arquivo client e atualiza atributos correspondentes
					arquivo_client.nome
					arquivo_client.caminho_completo
					arquivo_client.extensao_tipo ==> em 14/05/19: virou atributo calculado (property)
					arquivo_client.tem_no_vendor = True
			"""
			file_client = configuracaogeral.path_repositorio_client+arquivo_vendor.caminho_completo
			arquivo_client.nome = ArquivoVendor.obter_apenas_nome(file_client)
			arquivo_client.caminho_completo = file_client.replace(configuracaogeral.path_repositorio_client,'')
			#arquivo_client.extensao_tipo = ArquivoVendor.obter_extensao_tipo(arquivo_client.nome)			
			arquivo_client.tem_no_vendor = True

			"""
				- verifica se são iguais
			"""
			if filecmp.cmp(configuracaogeral.path_repositorio_vendor+arquivo_vendor.caminho_completo, \
				configuracaogeral.path_repositorio_client+arquivo_client.caminho_completo):
				"""
					- se forem iguais:
						arquivo_vendor.igual_ao_client = True
						arquivo_client.igual_ao_vendor = True
				"""
				arquivo_vendor.igual_ao_client = True
				arquivo_client.igual_ao_vendor = True
			else:
				"""
					- se não forem iguais
						arquivo_vendor.igual_ao_client = False
						arquivo_client.igual_ao_vendor = False
				"""
				arquivo_vendor.igual_ao_client = False
				arquivo_client.igual_ao_vendor = False
				"""
				- salva o arquivo_client
					arquivo_client.save()
				"""
			arquivo_client.save()

		"""
		- salva o arquivo_vendor
			arquivo_vendor.save()
		"""
		arquivo_vendor.save()


		# Em 14/05/19: só persiste objetos do tipo Commit se houver diferenças entre os arquivos vendor e client #
		if arquivo_client and not arquivo_vendor.igual_ao_client:
			lista_commits_client = git_client.get_commits_modified_file(arquivo_client.caminho_completo)
			for c in lista_commits_client:
				obj, created = Commit.objects.get_or_create(string_hash=c)
				arquivo_client.commits.add(obj)

			lista_commits_vendor = git_vendor.get_commits_modified_file(arquivo_vendor.caminho_completo)
			for c in lista_commits_vendor:
				obj, created = Commit.objects.get_or_create(string_hash=c)
				arquivo_vendor.commits.add(obj)


		"""
		- cria um objeto ArquivosComparados
			arquivos_comparados.comparacao = comparacao
			arquivos_comparados.arquivo_vendor = arquivo_vendor
			arquivos_comparados.arquivo_client = arquivo_client
		- salva o objeto ArquivosComparados
			arquivos_comparados.save()
		"""
		arquivos_comparados = ArquivosComparados()
		arquivos_comparados.comparacao = comparacao
		arquivos_comparados.arquivo_vendor = arquivo_vendor
		arquivos_comparados.arquivo_client = arquivo_client
		
		# Em 17/05/19: busca nº de linhas incluídas e excluídas via comando do git para arquivos diferentes#
		if arquivo_vendor.tem_no_client and not arquivo_vendor.igual_ao_client and not arquivos_comparados.eh_binario():
			detalhes_diff = buscar_detalhes_diff_entre_arquivos(configuracaogeral.path_repositorio_vendor+\
				arquivo_vendor.caminho_completo, configuracaogeral.path_repositorio_client+arquivo_client.caminho_completo)
			if len(detalhes_diff) >= 3:
				arquivos_comparados.numero_linhas_inseridas = detalhes_diff[0]
				arquivos_comparados.numero_linhas_excluidas = detalhes_diff[1]
		arquivos_comparados.save()

		print('#', end="")

	comparacao.numero_arquivos_ignorados = numero_arquivos_ignorados
	comparacao.save()
	print('#')
	task = ThreadTask.objects.get(pk=task_id)
	task.is_done = True
	task.save()
	print("Finishing task",task_id)



def visualizar_comparacao_repositorios(request, id = None):

	comparacao_id = None
	# arquivos_comparados = None
	# form = None

	# busca todas as comparações já realizadas
	comparacao_choices = Comparacao.objects.all().order_by('-datahorario_execucao')
	comparacao_choices_to_choicefield = list()
	for comparacao in comparacao_choices:
		comparacao_choices_to_choicefield.append([comparacao.pk,comparacao])

	if request.method == 'GET':
		vet_teste = request.path.split('/')
		if vet_teste[len(vet_teste)-1] != '':
			comparacao_id = vet_teste[len(vet_teste)-1]

	# se POST será necessário processar os dados do formulário
	if request.method == 'POST' or comparacao_id:

		if comparacao_id:
			comparacao_escolhida = comparacao_id

		elif 'comparacao_escolhida' in request.POST:
			comparacao_escolhida = request.POST['comparacao_escolhida']

		else:
			messages.error(request, 'ID não informado')
			return render(request, 'index.html', {'subtitle': 'Bem-vindo', })

		# busca a configuração para o id informado
		comparacao_obj = Comparacao.objects.get(pk=comparacao_escolhida)

		# busca os pares de arquivos comparados
		arquivos_comparados = comparacao_obj.get_arquivos_comparados()
		diff_comparados = comparacao_obj.get_arquivos_comparados(somente_diferentes=True)
		
		comparados_por_tipo_dict = comparacao_obj.get_agrupados_por_tipo()
		comparados_por_tipo = comparados_por_tipo_dict['tipos_de_arquivos_identificados']
		comparados_por_tipo_total = comparados_por_tipo_dict['total']

		diff_por_tipo_dict = comparacao_obj.get_agrupados_por_tipo(somente_diferentes=True)
		diff_por_tipo = diff_por_tipo_dict['tipos_de_arquivos_identificados']
		diff_por_tipo_total = diff_por_tipo_dict['total']

		comparados_por_modulo_dict = comparacao_obj.get_agrupados_por_modulo()
		comparados_por_modulo = comparados_por_modulo_dict['modulos_identificados']
		comparados_por_modulo_total = comparados_por_modulo_dict['total']

		diff_por_modulo_dict = comparacao_obj.get_agrupados_por_modulo(somente_diferentes=True)
		diff_por_modulo = diff_por_modulo_dict['modulos_identificados']
		diff_por_modulo_total = diff_por_modulo_dict['total']

		diff_por_commit_dict = comparacao_obj.get_agrupados_por_commit(somente_diferentes=True)
		diff_por_commit = diff_por_commit_dict['commits_identificados']
		diff_por_commit_total = diff_por_commit_dict['total']

		
	# se GET cria o formulário em branco
	else:
		form = VisualizarComparacaoRepositoriosForm(comparacao_choices_to_choicefield)

	title = 'Forkuptool'
	subtitle = 'Visualizar comparação entre repositórios'
	return render(request, 'visualizar_comparacao_repositorios.html', locals())



def visualizar_analise_diferencas(request, id):
	comparacao_obj = get_object_or_404(Comparacao, pk=id)
	diff_comparados = comparacao_obj.get_arquivos_comparados(somente_diferentes=True)
	title = 'Forkuptool'
	subtitle = 'Visualizar análise de diferenças'
	return render(request, 'visualizar_analise_diferencas.html', locals())



def visualizar_diff_entre_arquivos(request, id):
	arquivos_comparados = ArquivosComparados.objects.get(pk=id)
	outputpath = diff2HtmlCompare.generateDiff2Html(arquivos_comparados.comparacao.path_repositorio_vendor+ \
		arquivos_comparados.arquivo_vendor.caminho_completo, \
		arquivos_comparados.comparacao.path_repositorio_client+arquivos_comparados.arquivo_client.caminho_completo)

	diff2HtmlCompare.showDiff(outputpath)
	return redirect('visualizar_comparacao_repositorios', id=arquivos_comparados.comparacao.id)
