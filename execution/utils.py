
from django.conf import settings

from .utils_ast import LinesFinder, Analyzer


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



# Retorna os nós do tipo informado através do método 'get_nohs' da classe Analyzer,
# que retorna qualquer nó existente na árvore e sub-árvores da AST do arquivo
def get_nohs(tipo_noh, full_name_arquivo):
	# caminha na ast do arquivo
	finder = LinesFinder(full_name_arquivo)
	tree = finder.get_tree()
	if not tree:
		return None

	analyzer = Analyzer()
	analyzer.visit(tree)
    
    # retorna os nohs de acordo com o tipo
	nohs = None
	if tipo_noh == 'nohs_import':
		nohs = analyzer.get_nohs('import')
		nohs.sort()

	elif tipo_noh == 'nohs_import_from':
		nohs = analyzer.get_nohs('import_from')

	return nohs



def to_string_nohs(tipo_noh, nohs):
	if tipo_noh == 'nohs_import':
		return to_string_nohs_import(nohs)

	elif tipo_noh == 'nohs_import_from':
		return to_string_nohs_import_from(nohs)

	else:
		return None



def to_string_nohs_import(nohs):
	nohs_import_str = []
	for noh in nohs:
		nohs_import_str.append('import '+noh)
	str_import = '\n'
	str_import = str_import.join(nohs_import_str)
	return str_import



def to_string_nohs_import_from(nohs):
	nohs_import_from_str = []

	lista_keys = list(nohs.keys())
	lista_keys.sort()

	for key in lista_keys:
		modulo = key
		imports_do_modulo = nohs[key]
		imports_do_modulo.sort()
		str_imports_do_modulo = None
		str_imports_do_modulo = ', '
		str_imports_do_modulo = str_imports_do_modulo.join(imports_do_modulo)
		str_imports_do_modulo = 'from '+modulo+' import '+str_imports_do_modulo
		# quebrando linhas em 80 colunas
		vet_tmp = str_imports_do_modulo.split(', ')
		vet_tmp.reverse()
		vet_tmp2 = []
		while len(vet_tmp) > 0: 
			linha_da_vez = '' 
			linha_da_vez = vet_tmp.pop()+',' 
			if len(linha_da_vez) <= 80: 
				buscar_proximo_e_concatenar = True
				while buscar_proximo_e_concatenar: 
					if len(vet_tmp) > 0: 
						linha_da_vez = linha_da_vez+' '+vet_tmp.pop()+',' 
						if len(linha_da_vez) > 80: 
							if not linha_da_vez.startswith('from '):
								linha_da_vez = '    '+linha_da_vez
							linha_da_vez = linha_da_vez+ ' \\' 
							buscar_proximo_e_concatenar = False 
					else: 
						if not linha_da_vez.startswith('from '):
							linha_da_vez = '    '+linha_da_vez
						linha_da_vez = linha_da_vez+' \\' 
						buscar_proximo_e_concatenar = False 
			else: 
				linha_da_vez = linha_da_vez+' \\' 
			vet_tmp2.append(linha_da_vez) 
		# transformando novamente em string
		str_imports_do_modulo = None
		str_imports_do_modulo = '\n'
		str_imports_do_modulo = str_imports_do_modulo.join(vet_tmp2)
		str_imports_do_modulo = str_imports_do_modulo.rstrip(', \\')
		nohs_import_from_str.append(str_imports_do_modulo)

	str_import_from = '\n'
	str_import_from = str_import_from.join(nohs_import_from_str)
	return str_import_from



def rewrite_bloco_imports(nome_arquivo, novo_bloco):
	# procura pelo início e fim do bloco de imports no arquivo informado
	finder = LinesFinder(nome_arquivo)
	inicio_e_fim = finder.encontrar_inicio_e_fim_de_bloco_import()
	inicio = inicio_e_fim[0]
	fim = inicio_e_fim[1]
	if inicio is None or fim is None:
		print(('Problemas ao determininar início e fim de bloco de imports no arquivo {}').format(full_name_arquivo))
		return False
	
	# abre o arquivo para leitura
	linhas = ler_conteudo_de_arquivo(nome_arquivo)
	if not linhas:
		print(('Erro ao tentar ler conteúdo do arquivo {}').format(nome_arquivo))
		return False

	# converte o 'novo_bloco' para o formato esperado pela função (list)
	vet_tmp = novo_bloco.split('\n')
	novo_bloco = []
	for linha in vet_tmp:
		novo_bloco.append(linha+'\n')
	novo_bloco.append('\n\n')

	# fatia as linhas do arquivo resultando em 2 ou 3 pedaços, e os une em um novo conteúdo
	novo_conteudo = None
	if inicio == 1:
		# 2 pedaços - pedaço a ser substituído está no começo do arquivo
		fatia_de_interesse = linhas[fim:]
		novo_conteudo = novo_bloco + fatia_de_interesse

	elif len(linhas) == fim:
		# 2 pedaços - pedaço a ser substituído está no final do arquivo
		fatia_de_interesse = linhas[0:inicio]
		novo_conteudo = fatia_de_interesse + novo_bloco

	else:
		# 3 pedaços - pedaço a ser substituído está no meio do arquivo
		fatia_de_interesse_1 = linhas[0:(inicio-1)]
		fatia_de_interesse_2 = linhas[fim:]
		novo_conteudo = fatia_de_interesse_1 + novo_bloco + fatia_de_interesse_2

	# abre novamente o arquivo, agora para escrita, escrevendo o novo conteúdo
	if novo_conteudo:
		return escrever_conteudo_em_arquivo(nome_arquivo, novo_conteudo)
	else:
		return False

	# analise novamente o arquivo, agora buscando e removendo 'imports' soltos no código
	return remove_loose_imports(nome_arquivo)



def remove_loose_imports(nome_arquivo): 
    lineno_loose_imports = get_lineno_loose_imports(nome_arquivo)

    # só tenta manipular o arquivo se necessário
    if len(lineno_loose_imports) > 0:
        # abre o arquivo para leitura
        linhas = ler_conteudo_de_arquivo(nome_arquivo)

        # remove as linhas necessárias
        jah_removidos = 0
        for l in lineno_loose_imports:
            linhas.pop((l-1-jah_removidos))
            jah_removidos += 1

        try:
            with open(nome_arquivo, 'w') as arquivo:
                arquivo.writelines("%s" % linha for linha in linhas)
            arquivo.close()
        except IOError:
            print(('Erro ao tentar abrir o arquivo {} para escrita').format(nome_arquivo))
            return False
    return True



def get_lineno_loose_imports(nome_arquivo):
    lineno_loose_imports = []

	# caminha na ast do arquivo
    finder = LinesFinder(nome_arquivo)
    tree = finder.get_tree()
    if not tree:
        return None

    passou_pelo_bloco_principal = False
    for n in tree.body:
        if not (isinstance(n, ast.Import) or isinstance(n, ast.ImportFrom)) and not passou_pelo_bloco_principal:
            passou_pelo_bloco_principal = True

        if passou_pelo_bloco_principal:
            if isinstance(n, ast.Import) or isinstance(n, ast.ImportFrom):
                lineno_loose_imports.append(n.lineno)

    return lineno_loose_imports
