
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
