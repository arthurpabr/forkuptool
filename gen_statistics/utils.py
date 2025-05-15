

def get_numero_linhas_do_arquivo(arquivo):
	num_linhas = None
	try:
		with open(arquivo, 'r') as f:
			num_linhas = sum(1 for _ in f)
	except Exception as e:
		print(f'Erro ao ler {arquivo}: {e}')
	return num_linhas
