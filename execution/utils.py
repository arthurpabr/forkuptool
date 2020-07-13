
from django.conf import settings

from .utils_ast import LinesFinder


def ler_conteudo_de_arquivo(nome_arquivo):
	try:
		arquivo = open(nome_arquivo, 'r')
	except IOError:
		print(('Erro ao tentar abrir o arquivo {}').format(nome_arquivo))
		return False
	linhas = arquivo.readlines()
	arquivo.close()
	return linhas



def escrever_conteudo_em_arquivo(nome_arquivo, novo_conteudo):
	try:
		with open(nome_arquivo, 'w') as arquivo:
			arquivo.writelines("%s" % linha for linha in novo_conteudo)
		arquivo.close()
	except IOError:
		print(('Erro ao tentar abrir o arquivo {} para escrita').format(nome_arquivo))
		return False
	return True



def encontrar_inicio_e_fim_de_estrutura(nome_arquivo, unit): 
	# tenta identificar o início e fim da unidade de código "unit" no arquivo
	finder = LinesFinder(nome_arquivo)
	
	tipo_estrutura = ''
	# utiliza o modo "pytônico" para diferenciar 'classe' de 'função':
	# - classe iniciada em maiúsculo
	# - função iniciada em minúsculo
	vet_tmp = unit.split('::')
	if len(vet_tmp) == 2:
		return finder.encontrar_inicio_e_fim_de_metodo_em_classe(vet_tmp[1], vet_tmp[0])

	else: 
		if unit[0].isupper():
			return finder.encontrar_inicio_e_fim_de_classe(unit)

		else:
			return finder.encontrar_inicio_e_fim_de_funcao(unit)



# recebe linhas de início e fim no arquivo com nº de linhas iniciando em 1;
# devolve a fatia correspondente (tratando o índice da lista de linhas, que inicia em zero)
def get_slice_file(nome_arquivo, inicio_e_fim_da_fatia):
	inicio = inicio_e_fim_da_fatia[0]
	fim = inicio_e_fim_da_fatia[1]
	
	linhas = ler_conteudo_de_arquivo(nome_arquivo)
	if not linhas:
		print(('Erro ao tentar ler conteúdo do arquivo {}').format(nome_arquivo))
		return False

	if settings.DEBUG_1:
		print(('get_slice_file - Inicio: {} - Fim: {}').format(inicio,fim))
	return linhas[(inicio-1):fim]