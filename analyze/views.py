import json

from django.shortcuts import render
from pydriller import RepositoryMining, GitRepository
from datetime import datetime

from .forms import AnalisarTimelineForm
from configuration.models import ConfiguracaoFerramenta
from forkuptool.settings import LENGTH_INFO_CLIENT


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

			return render(request, 'analisar_timeline_show.html', locals())

	# se GET cria o formulário em branco
	form = AnalisarTimelineForm()
	subtitle = 'Analisar timeline'	
	return render(request, 'analisar_timeline.html', locals())
