
import filecmp
import os
import subprocess

from binaryornot.check import is_binary # para saber se um arquivo é binário ou não


def get_numero_linhas_do_arquivo(arquivo):
	num_linhas = None
	try:
		with open(arquivo, 'r') as f:
			num_linhas = sum(1 for _ in f)
	except Exception as e:
		print(f'Erro ao ler {arquivo}: {e}')
	return num_linhas


def pula_arquivo(file_name, file_full_name, extensoes_de_arquivos_a_ignorar):
	# pula arquivos binários
	eh_binario = is_binary(file_full_name)

	# pula determinadas extensões de arquivos
	eh_para_ignorar = False
	try:
		vet_tmp = file_name.split('.')
		file_extension = vet_tmp[len(vet_tmp)-1]
	except Exception as e:
		file_extension = None
	if file_extension and file_extension in extensoes_de_arquivos_a_ignorar:
		eh_para_ignorar = True

	return eh_binario or eh_para_ignorar


def identifica_app_name(FILE_PATH, file_name, file_full_name):
	app_name = file_full_name.replace(FILE_PATH,'')
	app_name = app_name.split('/')
	if len(app_name) > 1:
		app_name = app_name[1]
	else:
		app_name = app_name[0]

	if app_name == file_name:
		# não é um app, mas um arquivo na raíz
		app_name = '[raiz]'

	return app_name


def existe_este_arquivo(FILE_PATH, file_relative_name):
	return os.path.isfile(FILE_PATH+file_relative_name)


def arquivo_1_eh_igual_arquivo_2(FILE_PATH_1, file_relative_name_1, FILE_PATH_2, file_relative_name_2):
	return filecmp.cmp(FILE_PATH_1+file_relative_name_1, FILE_PATH_2+file_relative_name_2)


def count_diff_lines(diff_output):
	added = 0
	removed = 0
	context_changes = 0  # Para rastrear blocos de modificação

	for line in diff_output.split('\n'):
		if line.startswith('+') and not line.startswith('++'):
			added += 1
		elif line.startswith('-') and not line.startswith('--'):
			removed += 1
		elif line.startswith('@@'):
			context_changes += 1

	# Estima modificações como o mínimo entre adições e remoções
	modified = min(added, removed)
	added -= modified
	removed -= modified

	return {
		"adicionadas": added,
		"removidas": removed,
		"modificadas": modified
	}


def get_diff_stats(arquivo1, arquivo2):
	try:
		result = subprocess.run(['git','diff','--no-color',arquivo1,arquivo2], stdout=subprocess.PIPE)
		diff_output = result.stdout.decode('utf-8')
	except subprocess.CalledProcessError as e:
		print("Erro ao executar git diff:", e)
		return None

	return count_diff_lines(diff_output)

