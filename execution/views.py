import os

from django.conf import settings
from django.shortcuts import render

from .forms import ExecutarFerramentaForm
from .utils_parser import avaliar_patch_file
from .utils_refactor import buscar_sugestoes_refatoramento_patch_file
from configuration.models import ConfiguracaoFerramenta

def index(request):
    return render(request, 'execution.html', {'title': 'Forkuptool - Módulo de execução',
    	'subtitle': 'Módulo de execução da ferramenta de customização', 'messages': None, })



def executar_ferramenta(request):

	# busca as opções de configuração de execução da ferramenta registradas no banco de dados
	configuracaoferramenta_choices = ConfiguracaoFerramenta.objects.all().order_by('-id')
	configuracaoferramenta_choices_to_choicefield = list()
	for configuracao in configuracaoferramenta_choices:
		configuracaoferramenta_choices_to_choicefield.append([configuracao.pk,configuracao])

	# se GET cria o formulário em branco
	if request.method == 'GET':
		form = ExecutarFerramentaForm(configuracaoferramenta_choices_to_choicefield)
		subtitle = 'Executar ferramenta de customização'
		return render(request, 'executar_ferramenta.html', locals())


	# se POST será necessário processar os dados do formulário
	elif request.method == 'POST':
		configuracaoferramenta_escolhida = None

		if 'configuracaoferramenta_escolhida' in request.POST:
			configuracaoferramenta_escolhida = request.POST['configuracaoferramenta_escolhida']

		if configuracaoferramenta_escolhida:
			# busca a configuração para o id informado
			configuracaoferramenta_obj = ConfiguracaoFerramenta.objects.get(pk=configuracaoferramenta_escolhida)

			PATH_PATCH_FILES = configuracaoferramenta_obj.path_patch_files.replace('aliasprojeto',configuracaoferramenta_obj.alias_project)
			
			# navega pelo diretório dos arquivos de patch, buscando os arquivos .dsl
			resultado_processamento_por_arquivo = {}
			sugestoes_refatoramento_por_arquivo = {}
			for dirpath, dirnames, files in os.walk(PATH_PATCH_FILES):
				for file_name in sorted(files):
			 		file_full_name = os.path.join(dirpath, file_name)
			 		try:
			 			vet_tmp = file_name.split('.')
			 			file_extension = vet_tmp[len(vet_tmp)-1]
			 		except Exception as e:
			 			file_extension = None

			 		if file_extension and file_extension == 'dsl':
			 			print(('Encontrado arquivo dsl: {} (caminho completo: {})').format(file_name, file_full_name))
			 			resultados_execucao = avaliar_patch_file(file_name,configuracaoferramenta_obj)
			 			if settings.REFACTORY_SUGGESTIONS_ENABLE:
			 				sugestoes_refatoramento = buscar_sugestoes_refatoramento_patch_file(file_name,configuracaoferramenta_obj)
			 				sugestoes_refatoramento_por_arquivo[file_name] = sugestoes_refatoramento
		 				resultado_processamento_por_arquivo[file_name] = resultados_execucao

			subtitle = 'Resultados de execução'
			return render(request, 'executar_ferramenta_show.html', locals())

		else:
			messages.error(request, 'Necessário informar configuração para execução da ferramenta')
			return render(request, 'index.html', {'title': 'Forkuptool', 'subtitle': 'Bem-vindo', })
