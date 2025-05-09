import os

from django.conf import settings
from .utils_transformer import replace_string_em_arquivo, replace_string_em_unit, \
	replace_file, rewrite_imports, replace_unit, remove_string_em_unit, \
	remove_string_em_arquivo, remove_unit, add_unit, remove_annotation, \
	add_annotation
from .utils_ast import LinesFinder


def avaliar_patch_file(nome_arquivo, configuracaoferramenta):
	print('################')
	print ('Entrando na rotina avaliar_patch_file')
	print('################')

	arq = open(configuracaoferramenta.path_patch_files+nome_arquivo, 'r')
	texto = arq.readlines()
	resultados_execucao = {}
	for linha in texto :
		linha = linha.rstrip('\n')
		if linha.startswith('#'):
			resultados_execucao[linha] = 'linha de comentário'
		else:
			print('Interpretar: '+linha)
			resultados_execucao[linha] = avaliar_instrucao(linha, configuracaoferramenta)
	arq.close()

	return resultados_execucao



def avaliar_instrucao(instruction_line, configuracaoferramenta):
	resultado_execucao = ''
	vet_tmp = instruction_line.split(' ')

	if len(vet_tmp) < 2:
		resultado_execucao = ('ERRO: instrução {} mal formulada').format(instruction_line)
		print(resultado_execucao)
		return resultado_execucao

	file = configuracaoferramenta.path_vendor+vet_tmp[0]
	instruction = vet_tmp[1]

	# 1º passo: verifica se o arquivo a ser customizado - file - existe ou não no projeto original
	if not os.path.isfile(file):
		resultado_execucao = ('ERRO: parâmetro \'file\' inválido - arquivo inexistente: {}').format(file)
		print(resultado_execucao)
		return resultado_execucao

	# 2º passo: verifica se o sufixo da instrução é válido
	if instruction not in settings.VALID_INSTRUCTIONS_SUFFIXES:
		resultado_execucao = ('ERRO: sufixo de instrução inválido: {}').format(instruction)
		print(resultado_execucao)
		return resultado_execucao

	# 3º passo: delega o processamento da instrução de acordo com o sufixo
	if instruction == 'add':
		return avaliar_instrucao_add(instruction_line, configuracaoferramenta)

	elif instruction == 'remove':
		return avaliar_instrucao_remove(instruction_line, configuracaoferramenta)

	elif instruction == 'replace':
		return avaliar_instrucao_replace(instruction_line, configuracaoferramenta)

	else:
		resultado_execucao = ('ERRO: sufixo de instrução inválido: {}').format(instruction)
		print(resultado_execucao)
		return resultado_execucao



def avaliar_instrucao_add(instruction_line, configuracaoferramenta):
	vet_tmp = instruction_line.split(' ')
	code_unit = vet_tmp[2]

	if code_unit.startswith('@'):
		return avaliar_instrucao_add_annotation(instruction_line, configuracaoferramenta)

	else:
		return avaliar_instrucao_add_unit(instruction_line, configuracaoferramenta)



def avaliar_instrucao_remove(instruction_line, configuracaoferramenta):
	vet_tmp = instruction_line.split(' ')
	code_unit = vet_tmp[2]

	if len(vet_tmp) == 5:
		if code_unit.startswith('@'):
			return avaliar_instrucao_remove_annotation(instruction_line, configuracaoferramenta)
		else:
			return avaliar_instrucao_remove_string(instruction_line, configuracaoferramenta)

	elif len(vet_tmp) == 3:
		if code_unit.startswith('"'):
			return avaliar_instrucao_remove_string(instruction_line, configuracaoferramenta)
		else:
			return avaliar_instrucao_remove_unit(instruction_line, configuracaoferramenta)

	else:
		if code_unit.startswith('"'):
			return avaliar_instrucao_remove_string(instruction_line, configuracaoferramenta)

		elif vet_tmp[2] == 'from':
			return avaliar_instrucao_remove_string(instruction_line, configuracaoferramenta)

		else:
			resultado_execucao = 'ERRO: instrução remove mal formulada'
			print(resultado_execucao)
			return resultado_execucao



def avaliar_instrucao_replace(instruction_line, configuracaoferramenta):
	vet_tmp = instruction_line.split(' ')

	if len(vet_tmp) == 2:
		return avaliar_instrucao_replace_file(instruction_line, configuracaoferramenta)

	elif len(vet_tmp) == 3:
		return avaliar_instrucao_replace_unit(instruction_line, configuracaoferramenta)

	else:
		if vet_tmp[2].startswith('@'):
			return avaliar_instrucao_replace_annotation(instruction_line, configuracaoferramenta)

		elif vet_tmp[2] == 'from' or vet_tmp[2].startswith('"'):
			return avaliar_instrucao_replace_string(instruction_line, configuracaoferramenta)

		else:
			resultado_execucao = 'ERRO: instrução replace mal formulada'
	print(resultado_execucao)
	return resultado_execucao



def avaliar_instrucao_add_annotation(instruction_line, configuracaoferramenta):
	resultado_execucao = ''
	vet_tmp = instruction_line.split(' ')
	file = configuracaoferramenta.path_vendor+vet_tmp[0]
	# passo 0: verifica se 'file' não gera erros de 
	# parser ao arregar a AST dos arquivos (problema ref. incompatibilidades entre
	# python 2.7 e python 3.x)
	check_file = LinesFinder.check_parser_ast(file)
	if not check_file[0]:
		msg = ('ERRO DE PARSER - arquivo {} com erros de parser na AST').format(file)
		msg+= ('\nErro na linha {} com erros de parser na AST\n').format(check_file[1])
		resultado_execucao = msg
		print(resultado_execucao)
		return resultado_execucao

	instruction = vet_tmp[1]
	annotation = vet_tmp[2]
	# da posição 3 em diante estarão representados os demais parâmetros, 
	# mas com tamanho arbitrário já que no Json podem haver n espaços;
	# é necessário reconstruir os parâmetros
	separator = ' '
	part_instruction = ''
	part_instruction = separator.join(vet_tmp[3:])
	# a string utilizada para separar o Json dos demais parâmetros foi 
	# definida empiricamente e é representada abaixo
	separator = '} to '
	vet_tmp = part_instruction.split(separator)
	str_json = vet_tmp[0]+'}'
	# remonta novamente os parâmetros restantes
	separator = ' '
	part_instruction = ''
	part_instruction = separator.join(vet_tmp[1:])
	vet_tmp = part_instruction.split(' ')
	code_unit_to = vet_tmp[0]
	position_ref = None
	annotation_ref = None
	if(len(vet_tmp) == 3):
		position_ref = vet_tmp[1]
		annotation_ref = vet_tmp[2]

	if position_ref:
		# verifica se a referência de posicionamento é válida
		if position_ref != 'before' and position_ref != 'after':
			resultado_execucao = ('Instrução add @annotation mal formulada - posição {} inválida').format(position_ref)
			print(resultado_execucao)
			return resultado_execucao

		# se informada um posicionamento de referência, deve existir obrigatoriamente
		# uma annotation de referência
		if not annotation_ref:
			resultado_execucao = ('Instrução add @annotation mal formulada - annotation de referência não informada')
			print(resultado_execucao)
			return resultado_execucao

	executou_corretamente = add_annotation(file, annotation, str_json, code_unit_to, position_ref, annotation_ref)
	if executou_corretamente:
		resultado_execucao = ('Instrução {} executada com sucesso').format(instruction_line)
		print(resultado_execucao)

	else:
		resultado_execucao = ('ERRO ao executar {}').format(instruction_line)
		print(resultado_execucao)
	return resultado_execucao



def avaliar_instrucao_add_unit(instruction_line, configuracaoferramenta):
	resultado_execucao = ''
	vet_tmp = instruction_line.split(' ')

	# 0 passo: verifica se a quantidade de parâmetros esperados está correta
	if len(vet_tmp) < 5:
		resultado_execucao = ('ERRO: instrução add unit mal formulada')
		print(resultado_execucao)
		return resultado_execucao

	file = configuracaoferramenta.path_vendor+vet_tmp[0]
	file_aux = configuracaoferramenta.path_auxiliary_files+vet_tmp[0]
	instruction = vet_tmp[1]
	code_unit = vet_tmp[2]
	position_ref = vet_tmp[3]
	code_unit_ref = vet_tmp[4]

	# 1º passo: verifica se o arquivo auxiliar - necessário para esta instrução - existe
	if not os.path.isfile(file_aux):
		resultado_execucao = ('ERRO: arquivo auxiliar inexistente: {}').format(file_aux)
		print(resultado_execucao)
		return resultado_execucao

	# 2º passo: verifica se 'file' e 'file_aux' não irão gerar erros de 
	# parser ao arregar a AST dos arquivos (problema ref. incompatibilidades entre
	# python 2.7 e python 3.x)
	check_file = LinesFinder.check_parser_ast(file)
	if not check_file[0]:
		msg = ('PRÉ PROCESSAMENTO falhou - arquivo {} com erros de parser na AST').format(file)
		msg+= ('\nErro na linha {} com erros de parser na AST\n').format(check_file[1])
		resultado_execucao = msg
		print(resultado_execucao)
		return resultado_execucao

	check_file = LinesFinder.check_parser_ast(file_aux)
	if not check_file[0]:
		msg = ('PRÉ PROCESSAMENTO falhou - arquivo {} com erros de parser na AST').format(file_aux)
		msg+= ('\nErro na linha {} com erros de parser na AST\n').format(check_file[1])
		resultado_execucao = msg
		print(resultado_execucao)
		return resultado_execucao

	# 3º passo: PRÉ PROCESSAMENTO obrigatório para esta instrução
	if not rewrite_imports(file, file_aux, 'both'):
		resultado_execucao = ('PRÉ PROCESSAMENTO falhou - arquivo {}').format(file)
		print(resultado_execucao)
		return resultado_execucao

	# 4º passo: verifica se a referência de posicionamento é válida
	if position_ref != 'before' and position_ref != 'after':
		resultado_execucao = ('Instrução add unit mal formulada - posição {} inválida').format(position_ref)
		print(resultado_execucao)
		return resultado_execucao

	executou_corretamente = add_unit(file, file_aux, code_unit, code_unit_ref, position_ref)
	if executou_corretamente:
		resultado_execucao = ('Instrução {} executada com sucesso').format(instruction_line)
		print(resultado_execucao)

	else:
		resultado_execucao = ('ERRO ao executar {}').format(instruction_line)
		print(resultado_execucao)
	return resultado_execucao



def avaliar_instrucao_remove_annotation(instruction_line, configuracaoferramenta):
	resultado_execucao = ''
	vet_tmp = instruction_line.split(' ')
	file = configuracaoferramenta.path_vendor+vet_tmp[0]
	# passo 0: verifica se 'file' não gera erros de 
	# parser ao arregar a AST dos arquivos (problema ref. incompatibilidades entre
	# python 2.7 e python 3.x)
	check_file = LinesFinder.check_parser_ast(file)
	if not check_file[0]:
		msg = ('ERRO DE PARSER - arquivo {} com erros de parser na AST').format(file)
		msg+= ('\nErro na linha {} com erros de parser na AST\n').format(check_file[1])
		resultado_execucao = msg
		print(resultado_execucao)
		return resultado_execucao

	instruction = vet_tmp[1]
	annotation = vet_tmp[2]
	code_unit_ref = vet_tmp[4]

	executou_corretamente = remove_annotation(file, annotation, code_unit_ref)
	if executou_corretamente:
		resultado_execucao = ('Instrução {} executada com sucesso').format(instruction_line)
		print(resultado_execucao)

	else:
		resultado_execucao = ('ERRO ao executar {}').format(instruction_line)
		print(resultado_execucao)
	return resultado_execucao



def avaliar_instrucao_remove_string(instruction_line, configuracaoferramenta):
	resultado_execucao = ''
	vet_tmp = instruction_line.split(' ')
	file = configuracaoferramenta.path_vendor+vet_tmp[0]
	# passo 0: verifica se 'file' não gera erros de 
	# parser ao arregar a AST dos arquivos (problema ref. incompatibilidades entre
	# python 2.7 e python 3.x)
	check_file = LinesFinder.check_parser_ast(file)
	if not check_file[0]:
		msg = ('ERRO DE PARSER - arquivo {} com erros de parser na AST').format(file)
		msg+= ('\nErro na linha {} com erros de parser na AST\n').format(check_file[1])
		resultado_execucao = msg
		print(resultado_execucao)
		return resultado_execucao

	instruction = vet_tmp[1]
	code_unit = None

	if vet_tmp[2] == 'from':
		code_unit = vet_tmp[3]

	full_string = ''
	if code_unit:
		# se informada a unidade de código (unit), a string a ser removida
		# está representas no vetor original - vet_tmp - a partir da posição 4
		separator = ' '
		full_string = separator.join(vet_tmp[4:])
	else:
		# caso contrário a string a ser removida está representada no vetor 
		# original - vet_tmp - a partir da posição 2
		separator = ' '
		full_string = separator.join(vet_tmp[2:])

	full_string = full_string.strip('"')

	if code_unit:
		executou_corretamente = remove_string_em_unit(file, code_unit, full_string)
		if executou_corretamente:
			resultado_execucao = ('Instrução {} executada com sucesso').format(instruction_line)
			print(resultado_execucao)

		else:
			resultado_execucao = ('ERRO ao executar {}').format(instruction_line)
			print(resultado_execucao)

	else:
		# trata-se de replace string em todo o arquivo
		executou_corretamente = remove_string_em_arquivo(file, full_string)
		if executou_corretamente:
			resultado_execucao = ('Instrução {} executada com sucesso').format(instruction_line)
			print(resultado_execucao)

		else:
			resultado_execucao = ('ERRO ao executar {}').format(instruction_line)
			print(resultado_execucao)

	return resultado_execucao



def avaliar_instrucao_remove_unit(instruction_line, configuracaoferramenta):
	resultado_execucao = ''
	vet_tmp = instruction_line.split(' ')
	file = configuracaoferramenta.path_vendor+vet_tmp[0]
	# passo 0: verifica se 'file' não gera erros de 
	# parser ao arregar a AST dos arquivos (problema ref. incompatibilidades entre
	# python 2.7 e python 3.x)
	check_file = LinesFinder.check_parser_ast(file)
	if not check_file[0]:
		msg = ('ERRO DE PARSER - arquivo {} com erros de parser na AST').format(file)
		msg+= ('\nErro na linha {} com erros de parser na AST\n').format(check_file[1])
		resultado_execucao = msg
		print(resultado_execucao)
		return resultado_execucao

	instruction = vet_tmp[1]
	code_unit = vet_tmp[2]

	executou_corretamente = remove_unit(file, code_unit)
	if executou_corretamente:
		resultado_execucao = ('Instrução {} executada com sucesso').format(instruction_line)
		print(resultado_execucao)

	else:
		resultado_execucao = ('ERRO ao executar {}').format(instruction_line)
		print(resultado_execucao)
	return resultado_execucao



def avaliar_instrucao_replace_file(instruction_line, configuracaoferramenta):
	resultado_execucao = ''
	vet_tmp = instruction_line.split(' ')
	file = configuracaoferramenta.path_vendor+vet_tmp[0]
	file_aux = configuracaoferramenta.path_auxiliary_files+vet_tmp[0]
	instruction = vet_tmp[1]

	# 1º passo: verifica se o arquivo auxiliar - necessário para esta instrução - existe
	if not os.path.isfile(file_aux):
		resultado_execucao = ('ERRO: arquivo auxiliar inexistente: {}').format(file_aux)
		print(resultado_execucao)
		return resultado_execucao	

	executou_corretamente = replace_file(file, file_aux)

	if executou_corretamente:
		resultado_execucao = ('Instrução {} executada com sucesso').format(instruction_line)
		print(resultado_execucao)

	else:
		resultado_execucao = ('ERRO ao executar {}').format(instruction_line)
		print(resultado_execucao)

	return resultado_execucao



def avaliar_instrucao_replace_unit(instruction_line, configuracaoferramenta):
	resultado_execucao = ''
	vet_tmp = instruction_line.split(' ')
	file = configuracaoferramenta.path_vendor+vet_tmp[0]
	file_aux = configuracaoferramenta.path_auxiliary_files+vet_tmp[0]
	instruction = vet_tmp[1]
	code_unit = vet_tmp[2]

	# 1º passo: verifica se o arquivo auxiliar - necessário para esta instrução - existe
	if not os.path.isfile(file_aux):
		resultado_execucao = ('ERRO: arquivo auxiliar inexistente: {}').format(file_aux)
		print(resultado_execucao)
		return resultado_execucao

	# 2º passo: verifica se 'file' e 'file_aux' não irão gerar erros de 
	# parser ao arregar a AST dos arquivos (problema ref. incompatibilidades entre
	# python 2.7 e python 3.x)
	check_file = LinesFinder.check_parser_ast(file)
	if not check_file[0]:
		msg = ('PRÉ PROCESSAMENTO falhou - arquivo {} com erros de parser na AST').format(file)
		msg+= ('\nErro na linha {} com erros de parser na AST\n').format(check_file[1])
		resultado_execucao = msg
		print(resultado_execucao)
		return resultado_execucao

	check_file = LinesFinder.check_parser_ast(file_aux)
	if not check_file[0]:
		msg = ('PRÉ PROCESSAMENTO falhou - arquivo {} com erros de parser na AST').format(file_aux)
		msg+= ('\nErro na linha {} com erros de parser na AST\n').format(check_file[1])
		resultado_execucao = msg
		print(resultado_execucao)
		return resultado_execucao

	# 3º passo: PRÉ PROCESSAMENTO obrigatório para esta instrução
	if not rewrite_imports(file, file_aux, 'both'):
		resultado_execucao = ('PRÉ PROCESSAMENTO falhou - arquivo {}').format(file)
		print(resultado_execucao)
		return resultado_execucao

	executou_corretamente = replace_unit(file, file_aux, code_unit)
	if executou_corretamente:
		resultado_execucao = ('Instrução {} executada com sucesso').format(instruction_line)
		print(resultado_execucao)

	else:
		resultado_execucao = ('ERRO ao executar {}').format(instruction_line)
		print(resultado_execucao)

	return resultado_execucao



def avaliar_instrucao_replace_annotation(instruction_line, configuracaoferramenta):
	resultado_execucao = ''
	vet_tmp = instruction_line.split(' ')
	file = configuracaoferramenta.path_vendor+vet_tmp[0]
	# passo 0: verifica se 'file' não gera erros de 
	# parser ao arregar a AST dos arquivos (problema ref. incompatibilidades entre
	# python 2.7 e python 3.x)
	check_file = LinesFinder.check_parser_ast(file)
	if not check_file[0]:
		msg = ('ERRO DE PARSER - arquivo {} com erros de parser na AST').format(file)
		msg+= ('\nErro na linha {} com erros de parser na AST\n').format(check_file[1])
		resultado_execucao = msg
		print(resultado_execucao)
		return resultado_execucao

	instruction = vet_tmp[1]
	annotation = vet_tmp[2]
	# da posição 3 em diante estarão representados os demais parâmetros, 
	# mas com tamanho arbitrário já que no Json podem haver n espaços;
	# é necessário reconstruir os parâmetros
	separator = ' '
	part_instruction = ''
	part_instruction = separator.join(vet_tmp[3:])
	# a string utilizada para separar o Json dos demais parâmetros foi 
	# definida empiricamente e é representada abaixo
	separator = '} from '
	vet_tmp = part_instruction.split(separator)
	str_json = vet_tmp[0]+'}'
	# remonta novamente os parâmetros restantes
	separator = ' '
	part_instruction = ''
	part_instruction = separator.join(vet_tmp[1:])
	vet_tmp = part_instruction.split(' ')
	code_unit_from = vet_tmp[0]
	position_ref = None
	annotation_ref = None

	finder = LinesFinder(file)
	annotation_ref = finder.get_nome_annotation_anterior(annotation, code_unit_from)
	print(('Annotation anterior: {}').format(annotation_ref))
	if annotation_ref:
		position_ref = 'after'
	
	executou_corretamente_remove = False
	executou_corretamente_add = False
	executou_corretamente_remove = remove_annotation(file, annotation, code_unit_from)
	if executou_corretamente_remove:
		executou_corretamente_add = add_annotation(file, annotation, str_json, code_unit_from, position_ref, annotation_ref)

	if executou_corretamente_remove and executou_corretamente_add:
		resultado_execucao = ('Instrução {} executada com sucesso').format(instruction_line)
		print(resultado_execucao)

	else:
		resultado_execucao = ('ERRO ao executar {}').format(instruction_line)
		print(resultado_execucao)
	return resultado_execucao



def avaliar_instrucao_replace_string(instruction_line, configuracaoferramenta):
	resultado_execucao = ''
	vet_tmp = instruction_line.split(' ')
	file = configuracaoferramenta.path_vendor+vet_tmp[0]
	# passo 0: verifica se 'file' não gera erros de 
	# parser ao arregar a AST dos arquivos (problema ref. incompatibilidades entre
	# python 2.7 e python 3.x)
	check_file = LinesFinder.check_parser_ast(file)
	if not check_file[0]:
		msg = ('ERRO DE PARSER - arquivo {} com erros de parser na AST').format(file)
		msg+= ('\nErro na linha {} com erros de parser na AST\n').format(check_file[1])
		resultado_execucao = msg
		print(resultado_execucao)
		return resultado_execucao

	instruction = vet_tmp[1]
	code_unit = None

	if vet_tmp[2] == 'from':
		code_unit = vet_tmp[3]

	full_strings = ''
	if code_unit:
		# se informada a unidade de código (unit), as strings str1 e str2 
		# estão representas no vetor original - vet_tmp - a partir da posição 4
		separator = ' '
		full_strings = separator.join(vet_tmp[4:])
	else:
		# caso contrário as strings str1 e str2 estão representadas no vetor 
		# original - vet_tmp - a partir da posição 2
		separator = ' '
		full_strings = separator.join(vet_tmp[2:])

	old_str = ''
	new_str = ''
	vet_tmp2 = full_strings.split(' by ')
	old_str = vet_tmp2[0].strip('"')
	new_str = vet_tmp2[1].strip('"')

	if code_unit:
		executou_corretamente = replace_string_em_unit(file, code_unit, old_str, new_str)
		if executou_corretamente:
			resultado_execucao = ('Instrução {} executada com sucesso').format(instruction_line)
			print(resultado_execucao)

		else:
			resultado_execucao = ('ERRO ao executar {}').format(instruction_line)
			print(resultado_execucao)

	else:
		# trata-se de replace string em todo o arquivo
		executou_corretamente = replace_string_em_arquivo(file, old_str, new_str)
		if executou_corretamente:
			resultado_execucao = ('Instrução {} executada com sucesso').format(instruction_line)
			print(resultado_execucao)

		else:
			resultado_execucao = ('ERRO ao executar {}').format(instruction_line)
			print(resultado_execucao)

	return resultado_execucao

