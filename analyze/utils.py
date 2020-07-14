import re
import subprocess

from django.http import JsonResponse
from configuration.models import ThreadTask
from execution.utils import ler_conteudo_de_arquivo



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



def contar_linhas_entre_esses_linhas_neste_arquivo(linha_1, linha_2, este_arquivo):
	linhas = ler_conteudo_de_arquivo(este_arquivo)
	contador = 0
	contar = False
	if linhas:
		for l in linhas:
			l = l.rstrip('\n')
			l = l.rstrip(' ')
			if l == linha_1:
				contar = True
			if contar:
				contador+=1
			if l == linha_2:
				contar = False
	return contador



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