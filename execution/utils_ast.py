
import ast

from verbalexpressions import VerEx


class LinesFinder():

    # construtor; inicializa 1 atributo:
    # - nome_arquivo: nome do arquivo onde serão realizadas as buscas e o parser da AST
	def __init__(self, nome_arquivo):
		self.nome_arquivo = nome_arquivo
		self.tree = None
		with open(self.nome_arquivo, 'r') as source:
			try:
				self.tree = ast.parse(source.read())
			except SyntaxError:
				print(('Erro de sintaxe no parser do arquivo {}').format(self.nome_arquivo))

	
	@staticmethod
	def check_parser_ast(nome_arquivo):
		ok = True
		erro = None
		with open(nome_arquivo, 'r') as source:
			try:
				tree = ast.parse(source.read())
			except Exception as e:
				erro = str(e.lineno)+' - '+e.msg+' - '+e.text
				ok = False
		return [ok,erro]



	def eh_linha_vazia(self, linha):
		tester = VerEx().\
			start_of_line().\
			end_of_line()
		teste_1 = tester.match(linha)
		teste_2 = tester.match(VerEx().find(' ').replace(linha, ''))
		teste_3 = linha == ''
		return (teste_1 is not None) or (teste_2 is not None) or teste_3


	def get_tree(self):
		return self.tree


	def encontrar_inicio_e_fim_de_bloco_import(self): 
		linha_inicio = None
		linha_fim = None

		if not self.tree:
			return None

		for n in self.tree.body:
			if not linha_inicio:
				if isinstance(n, ast.Import) or isinstance(n, ast.ImportFrom):
					linha_inicio = n.lineno
			if not (isinstance(n, ast.Import) or isinstance(n, ast.ImportFrom)) and not linha_fim:
				linha_fim = (n.lineno-1)
		return [linha_inicio,linha_fim]


	def encontrar_inicio_e_fim_de_annotation(self, nome_annotation, nome_funcao):
		linha_inicio = None
		linha_fim = None

		if not self.tree:
			return None

		noh_alvo = None
		analyzer = Analyzer()
		analyzer.visit(self.tree)
		noh_alvo = analyzer.get_nohAnnotation(nome_funcao, nome_annotation.replace('@',''))

		if noh_alvo:
			linha_inicio = noh_alvo.lineno
			if 'args' in noh_alvo.__dict__:
				if len(noh_alvo.args) > 0:
					linha_fim = noh_alvo.args[len(noh_alvo.args)-1].lineno
				else:
					linha_fim = linha_inicio
			else:
				linha_fim = linha_inicio
		
		return [linha_inicio,linha_fim]


	def encontrar_inicio_e_fim_de_funcao(self, nome_funcao):
		return self.encontrar_inicio_e_fim_de_noh_ast(self.tree, ast.FunctionDef, nome_funcao)


	def encontrar_inicio_e_fim_de_classe(self, nome_classe):
		return self.encontrar_inicio_e_fim_de_noh_ast(self.tree, ast.ClassDef, nome_classe)


	def encontrar_inicio_e_fim_de_metodo_em_classe(self, nome_metodo, nome_classe):
		noh_classe = None
		analyzer = Analyzer()
		analyzer.visit(self.tree)
		# busca pelo nó correspondente à classe passada como parâmetro
		noh_classe = analyzer.get_nohClassDef(nome_classe)
		if not noh_classe:
			return None
		# busca pela final da classe, necessária no cálculo da linha final do método
		linha_inicial_final_da_classe = self.encontrar_inicio_e_fim_de_classe(nome_classe)
		if not linha_inicial_final_da_classe:
			return None
		linha_final_da_classe = linha_inicial_final_da_classe[1]
		# encontrado o nó da classe, busca pelo nó do método dentro da subárvore da classe
		return self.encontrar_inicio_e_fim_de_noh_ast(noh_classe, ast.FunctionDef, nome_metodo, linha_final_da_classe)


	def encontrar_inicio_e_fim_de_classe_em_factory(self, nome_classe, nome_factory):
		noh_factory = None
		analyzer = Analyzer()
		analyzer.visit(self.tree)
		# busca pelo nó correspondente à factory passada como parâmetro
		noh_factory = analyzer.get_nohFunctionDef(nome_factory)
		if not noh_factory:
			return None
		# busca pela final da factory, necessária no cálculo da linha final da classe
		linha_inicial_final_da_factory = self.encontrar_inicio_e_fim_de_funcao(nome_factory)
		if not linha_inicial_final_da_factory:
			return None
		linha_final_da_factory = linha_inicial_final_da_factory[1]
		# encontrado o nó da classe, busca pelo nó do método dentro da subárvore da classe
		return self.encontrar_inicio_e_fim_de_noh_ast(noh_factory, ast.ClassDef, nome_classe, linha_final_da_factory)



	def encontrar_inicio_e_fim_de_metodo_em_classe_em_factory(self, nome_metodo, nome_classe, nome_factory):
		noh_factory = None
		analyzer = Analyzer()
		analyzer.visit(self.tree)
		# busca pelo nó correspondente à factory passada como parâmetro
		noh_factory = analyzer.get_nohFunctionDef(nome_factory)
		if not noh_factory:
			return None
		# busca pelo nó correspondente à classe passada como parâmetro
		noh_classe = None
		analyzer2 = Analyzer()
		analyzer2.visit(noh_factory)
		noh_classe = analyzer2.get_nohClassDef(nome_classe)
		if not noh_classe:
			return None
		# busca pela final da classe, necessária no cálculo da linha final do método
		linha_inicial_final_da_classe = self.encontrar_inicio_e_fim_de_noh_ast(noh_factory, ast.ClassDef, nome_classe)
		if not linha_inicial_final_da_classe:
			return None
		linha_final_da_classe = linha_inicial_final_da_classe[1]
		# encontrado o nó da classe, busca pelo nó do método dentro da subárvore da classe
		return self.encontrar_inicio_e_fim_de_noh_ast(noh_classe, ast.FunctionDef, nome_metodo, linha_final_da_classe)



	def encontrar_inicio_e_fim_de_classe_em_classe(self, nome_classemetodo, nome_classe):
		noh_classe = None
		analyzer = Analyzer()
		analyzer.visit(self.tree)
		# busca pelo nó correspondente à classe passada como parâmetro
		noh_classe = analyzer.get_nohClassDef(nome_classe)
		if not noh_classe:
			return None
		# busca pela final da classe, necessária no cálculo da linha final do método
		linha_inicial_final_da_classe = self.encontrar_inicio_e_fim_de_classe(nome_classe)
		if not linha_inicial_final_da_classe:
			return None
		linha_final_da_classe = linha_inicial_final_da_classe[1]
		# encontrado o nó da classe, busca pelo nó do método dentro da subárvore da classe
		return self.encontrar_inicio_e_fim_de_noh_ast(noh_classe, ast.ClassDef, nome_classemetodo, linha_final_da_classe)



	# retorna o nº das linhas de início e fim da função indicada no arquivo indicado (nº de linhas iniciando em 1)
	def encontrar_inicio_e_fim_de_noh_ast(self, arvore_de_busca, tipo_do_noh, nome_da_estrutura, delimitador_linha_final = 0): 
		linha_inicio = None
		linha_fim = None
		if not arvore_de_busca:
			return None

		noh_alvo = None
		numero_de_nohs_filhos = len(arvore_de_busca.body)
		numero_noh_alvo = 0
		contador_de_nohs = 0
		for n in arvore_de_busca.body:
			contador_de_nohs += 1
			if isinstance(n, tipo_do_noh):
				if n.name == nome_da_estrutura:
					noh_alvo = n
					numero_noh_alvo = contador_de_nohs
					break

		# se não encontrado um noh para a função indicada, retorna None
		if not noh_alvo:
			# se não informado delimitador trata-se de busca por função ou classe
			if delimitador_linha_final == 0: 
				print(('Função/Classe {} não encontrada no arquivo {} ').format(nome_da_estrutura, self.nome_arquivo))
				return None
			# se informado delimitador trata-se de busca por método dentro de uma classe
			else:
				print(('Método {} da classe {} não encontrada no arquivo {} ').format(nome_da_estrutura, arvore_de_busca.name, self.nome_arquivo))
				return None

		linha_inicio = noh_alvo.lineno
		# abre novamente o arquivo, para contar o número de linhas e guardá-las para uso futuro, se necessário
		try:
			arquivo = open(self.nome_arquivo, 'r')
		except IOError:
			print(('Erro ao tentar abrir o arquivo {}').format(self.nome_arquivo))
			return None
			
		linhas = arquivo.readlines()
		arquivo.close()

		# se o nó alvo é o último nó da árvore, implica que a linha final da função/classe é a linha final do arquivo, SE 
		# informada a árvore completa; senão, é a última linha da subárvore analisada, informada no parâmetro 'delimitador_linha_final'
		if numero_noh_alvo == numero_de_nohs_filhos:
			if delimitador_linha_final == 0:
				linha_fim = len(linhas)
			else:
				linha_fim = delimitador_linha_final
		
		# se o nó alvo não é o último nó da árvore, implica que a linha final da função é a primeira linha em branco 
		# imediatamente anterior à linha de início do próximo nó
		else:
			linha_fim_candidata = arvore_de_busca.body[numero_noh_alvo].lineno
			linhas_para_analise = linhas[0:linha_fim_candidata]
			# inverte as linhas que serão analisadas
			linhas_para_analise.reverse()
			# caminha nas linhas, procurando uma linha vazia
			for l in linhas_para_analise:
				linha_fim_candidata -= 1
				if self.eh_linha_vazia(l):
					break
			linha_fim = linha_fim_candidata

		if linha_inicio > linha_fim:
			print(('Erro - linha inicial - {} - maior que linha final - {}').format(linha_inicio,linha_fim))
			return None

		return [linha_inicio,linha_fim]



class Analyzer(ast.NodeVisitor):

    # construtor; inicializa 3 atributos:
    # - uma lista que guarda NOMES de nós do tipo 'Import'
    # - um dicionário que guarda NOMES de nós to tipo 'ImportFrom'
    # - uma lista que guarda os NÓS do tipo 'FunctionDef'
    # - uma lista que guarda os NÓS do tipo 'ClassDef'
    def __init__(self):
        self.nohs_import = []
        self.nohs_import_from = {}
        self.nohs_function_def = []
        self.nohs_class_def = []


    # analisa só linhas de "import"
    def visit_Import(self, node):
        for alias in node.names:
            if alias.asname:
                self.nohs_import.append(alias.name+' as '+alias.asname)
            else:
                self.nohs_import.append(alias.name)
        self.generic_visit(node)


    # analisa só linhas de "from ... import"
    def visit_ImportFrom(self, node):
        if node.module not in self.nohs_import_from:
            self.nohs_import_from[node.module] = []

        for alias in node.names:
            str_name = ''
            if alias.asname:
                str_name = alias.name+' as '+alias.asname
            else:
                str_name = alias.name
            if str_name not in self.nohs_import_from[node.module]:
                self.nohs_import_from[node.module].append(str_name)
        self.generic_visit(node)


    # analisa definições de funções
    def visit_FunctionDef(self, node):
        if node not in self.nohs_function_def:
            self.nohs_function_def.append(node)
        self.generic_visit(node)


	# analisa definições de classes
    def visit_ClassDef(self, node):
        if node not in self.nohs_class_def:
            self.nohs_class_def.append(node)
        self.generic_visit(node)


    # imprime os atributos em tela
    def report(self):
        pprint(self.nohs_import)
        pprint(self.nohs_import_from)


    # retorna os nós do tipo informado
    def get_nohs(self, tipo):
        if tipo == 'import':
            return self.nohs_import

        elif tipo == 'import_from':
            return self.nohs_import_from

        else:
            return None


	# retorna o nó correspondente à função do nome informado como parâmetro
	# CUIDADO! Se houver mais de uma definição de função com mesmo nome, vai retornar apenas 
	# a 1ª ocorrência da função dentro da AST do arquivo analisado
    def get_nohFunctionDef(self, nome_funcao):
    	noh = None
    	for n in self.nohs_function_def:
    		if n.name == nome_funcao:
    			noh = n
    			break
    	return noh


	# retorna o nó correspondente à classe do nome informado como parâmetro
	# CUIDADO! Se houver mais de uma definição de classe com mesmo nome, vai retornar apenas 
	# a 1ª ocorrência da classe dentro da AST do arquivo analisado
    def get_nohClassDef(self, nome_classe):
    	noh = None
    	for n in self.nohs_class_def:
    		if n.name == nome_classe:
    			noh = n
    			break
    	return noh



	# retorna o nó correspondente à annotation do nome informado na função informada
    def get_nohAnnotation(self, nome_funcao, nome_annotation):
        noh = None
        noh_funcao = self.get_nohFunctionDef(nome_funcao)
        if noh_funcao:
            if 'decorator_list' in noh_funcao.__dict__:
                for n in noh_funcao.decorator_list:
                    if isinstance(n, ast.Name):
                        if 'id' in n.__dict__:
                            if n.id == nome_annotation:
                                noh = n

                    if isinstance(n, ast.Call):
                        if 'func' in n.__dict__:
                            n2 = n.func

                            if isinstance(n2, ast.Attribute):
                                n3 = n2.value

                                if isinstance(n3, ast.Name):
                                    if 'id' in n3.__dict__:
                                        if n3.id == nome_annotation:
                                            noh = n	

                            if isinstance(n2, ast.Name):
                                if 'id' in n2.__dict__:
                                    if n2.id == nome_annotation:
                                        noh = n

        return noh

