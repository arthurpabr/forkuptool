import os

from django.shortcuts import render
from binaryornot.check import is_binary # para saber se um arquivo é binário ou não

from .forms import GerarEstatisticasForm
from .utils import get_numero_linhas_do_arquivo
from configuration.models import ConfiguracaoGeral

def index(request):
    return render(request, 'statistics.html', {'title': 'Forkuptool / IFSULDEMINAS - Módulo de estatísticas',
    	'subtitle': 'Módulo de geração e visualização de estatísticas de comparação entre repositórios', 'messages': None, })


def gerar_estatisticas(request):
	# busca as opções de configuração de execução da ferramenta registradas no banco de dados
	configuracao_choices = ConfiguracaoGeral.objects.all().order_by('-id')
	configuracao_choices_to_choicefield = list()
	for configuracao in configuracao_choices:
		configuracao_choices_to_choicefield.append([configuracao.pk,configuracao])

	# se GET cria o formulário em branco
	if request.method == 'GET':
		form = GerarEstatisticasForm(configuracao_choices_to_choicefield)
		subtitle = 'Gerar estatísticas de comparação'
		return render(request, 'gerar_estatisticas.html', locals())


	# se POST será necessário processar os dados do formulário
	elif request.method == 'POST':
		configuracao_escolhida = None

		if 'configuracao_escolhida' in request.POST:
			configuracao_escolhida = request.POST['configuracao_escolhida']

		if configuracao_escolhida:
			# busca a configuração para o id informado
			configuracao_obj = ConfiguracaoGeral.objects.get(pk=configuracao_escolhida)

			PATH_PRODUCTION_FILES = configuracao_obj.path_repositorio_client
			
			extensoes_de_arquivos_a_ignorar = ['pdf','PDF',]
			caminhos_para_ignorar = ['.git','.gitlab','deploy','__pycache__','docs_old','docs','workflows',]

			num_total_linhas_analisadas = 0
			arquivos_analisados = []
			arquivos_com_erro_ao_analisar = []
			for dirpath, dirnames, files in os.walk(PATH_PRODUCTION_FILES):

				# pula determinadas pastas
				dirnames[:] = [d for d in dirnames if d not in caminhos_para_ignorar]
				# pasta_atual = os.path.basename(dirpath)

				for file_name in sorted(files):
					file_full_name = os.path.join(dirpath, file_name)
					eh_binario = is_binary(file_full_name)
					
					# pula arquivos binários
					if eh_binario:
						continue

					# pula determinadas extensões de arquivos
					try:
						vet_tmp = file_name.split('.')
						file_extension = vet_tmp[len(vet_tmp)-1]
					except Exception as e:
						file_extension = None

					if file_extension and file_extension in extensoes_de_arquivos_a_ignorar:
						continue

					num_linhas = get_numero_linhas_do_arquivo(file_full_name)
					if num_linhas is None:
						arquivos_com_erro_ao_analisar.append(file_full_name)
					else:
						print(f'Arquivo {file_name} ({file_full_name}) - nº de linhas {num_linhas}')
						
						arquivos_analisados.append(file_full_name)
						num_total_linhas_analisadas += num_linhas

			print(f'Nº de arquivos analisados: {len(arquivos_analisados)}')
			print(f'Nº de linhas analisadas: {num_total_linhas_analisadas}')
			print(f'Nº de arquivos com erro ao analisar: {len(arquivos_com_erro_ao_analisar)}')

			subtitle = 'Resultados de execução'
			return render(request, 'gerar_estatisticas_show.html', locals())

		else:
			messages.error(request, 'Necessário informar configuração para execução da ferramenta')
			return render(request, 'index.html', {'title': 'Forkuptool', 'subtitle': 'Bem-vindo', })
