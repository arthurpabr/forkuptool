

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
			#resultados_execucao[linha] = avaliar_instrucao(linha, configuracaoferramenta)
	arq.close()

	return resultados_execucao
