
from .utils import ler_conteudo_de_arquivo, escrever_conteudo_em_arquivo, \
	encontrar_inicio_e_fim_de_estrutura, get_slice_file


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
	return escrever_conteudo_em_arquivo(nome_arquivo, novo_conteudo)



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

	# monta o novo conteúdo para a unit, substituindo a old_str pela new_str
	linhas_unit = get_slice_file(nome_arquivo, inicio_e_fim)
	novo_conteudo_unit = []
	for linha in linhas_unit:
		novo_conteudo_unit.append(linha.replace(old_str,new_str))

	# monta as novas linhas para o arquivo
	# abre o arquivo para leitura
	linhas = ler_conteudo_de_arquivo(nome_arquivo)
	if not linhas:
		print(('Erro ao tentar ler conteúdo do arquivo {}').format(nome_arquivo))
		return False
	trecho_1 = linhas[0:(inicio-1)]
	trecho_3 = linhas[fim:]

	novo_conteudo = trecho_1 + novo_conteudo_unit + trecho_3
	# abre novamente o arquivo, agora para escrita, escrevendo o novo conteúdo
	return escrever_conteudo_em_arquivo(nome_arquivo, novo_conteudo)

