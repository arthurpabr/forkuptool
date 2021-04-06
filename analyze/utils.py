import re
import subprocess

from django.http import JsonResponse
from configuration.models import ThreadTask
from execution.utils import ler_conteudo_de_arquivo
from pydriller import GitRepository 



def identificar_arquivos_em_conflito(linhas_de_erro):
	r_string = ' \S+[/]{1}\S+[\.]{1}\S+'
	er_busca = re.compile(r_string)
	arquivos_em_conflito = []
	for l in linhas_de_erro:
		if l.startswith('CONFLICT '):
			vet_busca = er_busca.findall(l)
			if len(vet_busca) > 0:
				arquivo = vet_busca[0].strip()
				arquivos_em_conflito.append(arquivo)
	return arquivos_em_conflito



def contar_ocorrencias_desta_linha_neste_arquivo(esta_linha, este_arquivo):
	linhas = ler_conteudo_de_arquivo(este_arquivo)
	contador = 0
	if linhas:
		for l in linhas:
			l = l.rstrip('\n')
			l = l.rstrip(' ')
			if l == esta_linha:
				contador+=1
	return contador



def identificar_intervalos_trechos_conflitantes(linha_1, linha_2, este_arquivo):
	linhas = ler_conteudo_de_arquivo(este_arquivo)
	ponteiro_atual = 0
	ponteiro_linha_inicio_intervalo = None
	intervalos = []
	if linhas:
		for l in linhas:
			ponteiro_atual+=1
			l = l.rstrip('\n')
			l = l.rstrip(' ')
			if l == linha_1:
				ponteiro_linha_inicio_intervalo = ponteiro_atual
			if l == linha_2:
				intervalos.append((ponteiro_linha_inicio_intervalo,ponteiro_atual))
				ponteiro_linha_inicio_intervalo = None
	return intervalos



def buscar_detalhes_diff_entre_arquivos(caminho_completo_vendor, caminho_completo_client):
	result = subprocess.run(['git','diff','--numstat',caminho_completo_vendor,caminho_completo_client], stdout=subprocess.PIPE)
	result_as_string = result.stdout.decode('utf-8')
	print(result_as_string)
	return result_as_string.split('\t')



def check_thread_task(request,id):
	print(id)
	is_done = False
	try:
		task = ThreadTask.objects.get(pk=id)
		is_done = task.is_done
	except Exception as e:
		pass
	return JsonResponse({'is_done':is_done})



def identificar_estatisticas_de_autores(gr, arquivo):
	equipe_dev = ['Wellington Openheimer Ribeiro','Robson Vitor Mendonça',\
		'Ricardo José de Araújo', 'Ricardo Jose Araujo', 'Ricardo Araujo',\
		'Paulo Humberto Rezende', 'Mauro Augusto Soares Rodrigues',\
		'Matheus Costa', 'Leonardo Aparecido Ciscon','Geovani Lopes',\
		'Arthur Roberto Marcondes']

	estatisticas = dict()
	estatisticas['ultimo_autor'] = None
	estatisticas['ultimo_autor_da_equipe'] = None
	estatisticas['maior_autor'] = None
	estatisticas['maior_autor_da_equipe'] = None

	autores = dict()
	autores_da_equipe = dict()

	# obtém a lista de commits que já modificaram o arquivo
	commits = gr.get_commits_modified_file(arquivo)
	for c in commits:
		commit_obj = gr.get_commit(c) 
		autor_da_vez = commit_obj.author.name.strip()
		if not estatisticas['ultimo_autor']:
			estatisticas['ultimo_autor'] = autor_da_vez 
		if autor_da_vez in autores: 
			autores[autor_da_vez]+=1 
		else: 
			autores[autor_da_vez] = 1 
		if autor_da_vez in equipe_dev: 
			if not estatisticas['ultimo_autor_da_equipe']: 
				estatisticas['ultimo_autor_da_equipe'] = autor_da_vez 
			if autor_da_vez in autores_da_equipe: 
				autores_da_equipe[autor_da_vez]+=1 
			else: 
				autores_da_equipe[autor_da_vez] = 1

	estatisticas['maior_autor'] = identificar_maior_autor(autores)
	estatisticas['maior_autor_da_equipe'] = identificar_maior_autor(autores_da_equipe)
	
	return estatisticas



def identificar_maior_autor(autores):
	maior_autor = None
	ocorrencias_maior_autor = 0
	for key, value in autores.items(): 
		if value > ocorrencias_maior_autor: 
			ocorrencias_maior_autor = value 
			maior_autor = key

	return (maior_autor, ocorrencias_maior_autor)

