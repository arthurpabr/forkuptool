import subprocess

from .utils import ler_conteudo_de_arquivo, escrever_conteudo_em_arquivo, \
	encontrar_inicio_e_fim_de_estrutura, get_slice_file, get_nohs, to_string_nohs, \
	rewrite_bloco_imports


def rewrite_imports(nome_arquivo, nome_arquivo_auxiliar, where):
	# where: de onde as linhas de import devem ser buscadas
	# 		- both: de ambos arquivos (ORIGEM e AUXILIAR)
	# 		- source: do arquivo ORIGEM
	# 		- aux: do arquivo AUXILIAR

	nohs_import = None
	nohs_import_from = None
	rewrite_string = None

	if where == 'source':
		nohs_import = get_nohs('nohs_import', nome_arquivo)
		nohs_import_from = get_nohs('nohs_import_from', nome_arquivo)
		if nohs_import and nohs_import_from:
			str_1 = to_string_nohs('nohs_import', nohs_import)
			str_2 = to_string_nohs('nohs_import_from',nohs_import_from)
			rewrite_string = str_1+'\n'+str_2

	elif where == 'aux':
		nohs_import = get_nohs('nohs_import', nome_arquivo_auxiliar)
		nohs_import_from = get_nohs('nohs_import_from', nome_arquivo_auxiliar)
		if nohs_import and nohs_import_from:
			str_1 = to_string_nohs('nohs_import', nohs_import)
			str_2 = to_string_nohs('nohs_import_from',nohs_import_from)
			rewrite_string = str_1+'\n'+str_2

	elif where == 'both':
		# tem que trabalhar com os nós tanto do arquivo ORIGEM quanto do arquivo AUXILIAR
		nohs_import_arq_original = get_nohs('nohs_import', nome_arquivo)
		nohs_import_from_arq_original = get_nohs('nohs_import_from', nome_arquivo)

		nohs_import_arq_auxiliar = get_nohs('nohs_import', nome_arquivo_auxiliar)
		nohs_import_from_arq_auxiliar = get_nohs('nohs_import_from', nome_arquivo_auxiliar)

		if (not nohs_import_arq_original and not nohs_import_from_arq_original) or \
			(not nohs_import_arq_auxiliar and not nohs_import_from_arq_auxiliar):
			return False

		# trabalhando primeiro com nós do tipo import
		nohs_import_ambos = list()
		for noh in nohs_import_arq_original:
			if noh not in nohs_import_ambos:
				nohs_import_ambos.append(noh)
		for noh in nohs_import_arq_auxiliar:
			if noh not in nohs_import_ambos:
				nohs_import_ambos.append(noh)
		str_1 = to_string_nohs('nohs_import', nohs_import_ambos)

		# trabalhando agora com nós do tipo import_from
		# obtendo as chaves dos dicionários de cada arquivo
		keys_import_from_arq_original = list(nohs_import_from_arq_original.keys())
		keys_import_from_arq_original.sort()
		keys_import_from_arq_auxiliar = list(nohs_import_from_arq_auxiliar.keys())
		keys_import_from_arq_auxiliar.sort()

		# montando o dicionário resultado (dicionário de listas) - criando as chaves
		nohs_import_from_ambos = {}
		for key in keys_import_from_arq_original:
			if key not in nohs_import_from_ambos:
				nohs_import_from_ambos[key] = []

		for key in keys_import_from_arq_auxiliar:
			if key not in nohs_import_from_ambos:
				nohs_import_from_ambos[key] = []

		# montando o dicionário resultado (dicionário de listas) - inserindo itens nas listas
		for lista in nohs_import_from_ambos:
			if lista in nohs_import_from_arq_original:
				for item in nohs_import_from_arq_original[lista]:
					if item not in nohs_import_from_ambos[lista]:
						nohs_import_from_ambos[lista].append(item)

			if lista in nohs_import_from_arq_auxiliar:
				for item in nohs_import_from_arq_auxiliar[lista]:
					if item not in nohs_import_from_ambos[lista]:
						nohs_import_from_ambos[lista].append(item)

		str_2 = to_string_nohs('nohs_import_from',nohs_import_from_ambos)
		rewrite_string = str_1+'\n'+str_2

	if rewrite_string:
		return rewrite_bloco_imports(nome_arquivo, rewrite_string)

	# se achar até aqui é porque algum erro ocorreu; retorna False
	return False



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



def replace_file(nome_arquivo, nome_arquivo_auxiliar):
	print ('cmd linux: '+'cp -f '+nome_arquivo_auxiliar+' '+nome_arquivo)
	result = subprocess.run(['cp','-f',nome_arquivo_auxiliar,nome_arquivo], stdout=subprocess.PIPE)
	result_as_string = result.stdout.decode('utf-8')
	if result_as_string == '':
		return True
	else:
		return False



def replace_unit(nome_arquivo, nome_arquivo_auxiliar, unit):
	inicio_e_fim = encontrar_inicio_e_fim_de_estrutura(nome_arquivo_auxiliar, unit)
	if inicio_e_fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit, nome_arquivo_auxiliar))
		return False

	inicio = inicio_e_fim[0]
	fim = inicio_e_fim[1]
	if inicio is None or fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit, nome_arquivo_auxiliar))
		return False

 	# obtém o novo código para a unit a partir do arquivo auxiliar e guarda numa variável auxiliar
	novo_conteudo_unit = get_slice_file(nome_arquivo_auxiliar, inicio_e_fim)

 	# obtém o início e fim da unit no arquivo de destino
	inicio_e_fim = encontrar_inicio_e_fim_de_estrutura(nome_arquivo, unit)
	if inicio_e_fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit, nome_arquivo))
		return False

	inicio = inicio_e_fim[0]
	fim = inicio_e_fim[1]
	if inicio is None or fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit, nome_arquivo))
		return False

 	# monta as novas linhas para o arquivo de destino
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



def remove_string_em_unit(nome_arquivo, unit, string):
	inicio_e_fim = encontrar_inicio_e_fim_de_estrutura(nome_arquivo, unit)
	if inicio_e_fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit, nome_arquivo))
		return False

	inicio = inicio_e_fim[0]
	fim = inicio_e_fim[1]
	if inicio is None or fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit, nome_arquivo))
		return False

	# monta o novo conteúdo para a unit, substituindo a string por 'vazio'
	linhas_unit = get_slice_file(nome_arquivo, inicio_e_fim)
	novo_conteudo_unit = []
	for linha in linhas_unit:
		novo_conteudo_unit.append(linha.replace(string,''))

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



def remove_string_em_arquivo(nome_arquivo, string):
	# abre o arquivo para leitura
	linhas = ler_conteudo_de_arquivo(nome_arquivo)
	if not linhas:
		print(('Erro ao tentar ler conteúdo do arquivo {}').format(nome_arquivo))
		return False

	# monta o novo conteúdo para o arquivo, substituindo a string por 'vazio'
	novo_conteudo = []
	for linha in linhas:
		novo_conteudo.append(linha.replace(string,''))

	# abre novamente o arquivo, agora para escrita, escrevendo o novo conteúdo
	return escrever_conteudo_em_arquivo(nome_arquivo, novo_conteudo)



def remove_unit(nome_arquivo, unit):
	inicio_e_fim = encontrar_inicio_e_fim_de_estrutura(nome_arquivo, unit)
	if inicio_e_fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit, nome_arquivo))
		return False

	inicio = inicio_e_fim[0]
	fim = inicio_e_fim[1]
	if inicio is None or fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit, nome_arquivo))
		return False

 	# monta as novas linhas para o arquivo de destino, retirando o trecho referente à unit
 	# abre o arquivo para leitura
	linhas = ler_conteudo_de_arquivo(nome_arquivo)
	if not linhas:
		print(('Erro ao tentar ler conteúdo do arquivo {}').format(nome_arquivo))
		return False
	trecho_1 = linhas[0:(inicio-1)]
	trecho_3 = linhas[fim:]

	novo_conteudo = trecho_1 + trecho_3
 	# abre novamente o arquivo, agora para escrita, escrevendo o novo conteúdo
	return escrever_conteudo_em_arquivo(nome_arquivo, novo_conteudo)


def add_unit(nome_arquivo, nome_arquivo_auxiliar, unit, unit_ref, position_ref):
	inicio_e_fim = encontrar_inicio_e_fim_de_estrutura(nome_arquivo_auxiliar, unit)
	if inicio_e_fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit, nome_arquivo_auxiliar))
		return False

	inicio = inicio_e_fim[0]
	fim = inicio_e_fim[1]
	if inicio is None or fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit, nome_arquivo_auxiliar))
		return False

 	# obtém o código da nova unit a partir do arquivo auxiliar e guarda numa variável auxiliar
	nova_unit = get_slice_file(nome_arquivo_auxiliar, inicio_e_fim)

 	# obtém o início e fim da unit de referência no arquivo de destino
	inicio_e_fim = encontrar_inicio_e_fim_de_estrutura(nome_arquivo, unit_ref)
	if inicio_e_fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit_ref, nome_arquivo))
		return False

	inicio = inicio_e_fim[0]
	fim = inicio_e_fim[1]
	if inicio is None or fim is None:
		print(('Unidade de código {} NÃO ENCONTRADA no arquivo {} ').format(unit_ref, nome_arquivo))
		return False

 	# monta as novas linhas para o arquivo de destino
 	# abre o arquivo para leitura
	linhas = ler_conteudo_de_arquivo(nome_arquivo)
	if not linhas:
		print(('Erro ao tentar ler conteúdo do arquivo {}').format(nome_arquivo))
		return False

	# monta o novo conteúdo para o arquivo de acordo com a referência - antes ou depois
	# da unit_ref
	quebra_linha = ['\n\n',]
	trecho_2 = quebra_linha + nova_unit + quebra_linha
	if position_ref == 'before':
		trecho_1 = linhas[0:(inicio-1)]
		trecho_3 = linhas[inicio:]
	else:
		trecho_1 = linhas[0:fim]
		trecho_3 = linhas[fim:]

	novo_conteudo = trecho_1 + trecho_2 + trecho_3
 	# abre novamente o arquivo, agora para escrita, escrevendo o novo conteúdo
	return escrever_conteudo_em_arquivo(nome_arquivo, novo_conteudo)

