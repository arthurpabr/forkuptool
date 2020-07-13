
from .utils import ler_conteudo_de_arquivo, encontrar_inicio_e_fim_de_estrutura

def replace_string_em_arquivo(nome_arquivo, old_str, new_str):
	# abre o arquivo para leitura
	linhas = ler_conteudo_de_arquivo(nome_arquivo)
	if not linhas:
		print(('Erro ao tentar ler conteúdo do arquivo {}').format(nome_arquivo))
		return False

	# monta o novo conteúdo para o arquivo, substituindo a old_str pela new_str
	novo_conteudo = []
	for linha in linhas:
		novo_conteudo.append(linha.replace(old_str,new_str))

	# abre novamente o arquivo, agora para escrita, escrevendo o novo conteúdo
	try:
		with open(nome_arquivo, 'w') as arquivo:
			arquivo.writelines("%s" % linha for linha in novo_conteudo)
		arquivo.close()

	except IOError:
		print(('Erro ao tentar abrir o arquivo {} para escrita').format(nome_arquivo))
		return False

	return True



def replace_string_em_unit(nome_arquivo, unit, old_str, new_str):
	inicio_e_fim = encontrar_inicio_e_fim_de_estrutura(nome_arquivo, unit)
	if inicio_e_fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit, nome_arquivo))
		return False

	inicio = inicio_e_fim[0]
	fim = inicio_e_fim[1]
	if inicio is None or fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit, nome_arquivo))
		return False

	print(('Em implementação - início {} - fim {} ').format(inicio,fim))

