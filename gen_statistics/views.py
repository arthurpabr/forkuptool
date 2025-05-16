import base64
import os
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from django.shortcuts import render

from .forms import GerarEstatisticasForm
from .utils import (
	arquivo_1_eh_igual_arquivo_2, 
	existe_este_arquivo, 
	get_diff_stats,
	get_numero_linhas_do_arquivo, 
	identifica_app_name, 
	pula_arquivo,
)
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

			### Executa 2 verificações: repositório 1 para o repositório 2 e depois o contrário

			# configurações estáticas
			extensoes_de_arquivos_a_ignorar = ['pdf','PDF',]
			caminhos_para_ignorar = ['.git','.gitlab','deploy','__pycache__','docs_old','docs','workflows','lps',]
			apps_a_ignorar = ['static',]

			### Repositório 1 para o 2: master IFSULDEMINAS para merge-ifrn-xxx
			''' 
				Objetivos:
				- verificar quantos arquivos da master foram ALTERADOS na merge-ifrn-xxx
					- verificar nº de linhas ALTERADAS
					- verificar nº de linhas EXCLUÍDAS
					- verificar nº de linhas INCLUÍDAS
				- verificar quantos arquivos da master foram EXCLUÍDOS na merge-ifrn-xxx
				- contabilizar por MÓDULO (app)
			'''
			estatisticas_1_para_2 = dict()

			FILE_PATH = configuracao_obj.path_repositorio_client
			ANOTHER_FILE_PATH = configuracao_obj.path_repositorio_vendor

			arquivos_com_erro_ao_analisar = []
			for dirpath, dirnames, files in os.walk(FILE_PATH):
				# pula determinadas pastas
				dirnames[:] = [d for d in dirnames if d not in caminhos_para_ignorar]

				for file_name in sorted(files):
					file_full_name = os.path.join(dirpath, file_name)
					file_relative_name = file_full_name.replace(FILE_PATH,'')

					# pula o arquivo, se necessário
					if pula_arquivo(file_name, file_full_name, extensoes_de_arquivos_a_ignorar):
						continue	

					# identifica o app
					app_name = identifica_app_name(FILE_PATH, file_name, file_full_name)
					# pula o app, se for o caso (ex.: pasta 'static' que fica na raíz)
					if app_name in apps_a_ignorar:
						continue
					if app_name not in estatisticas_1_para_2.keys():
						estatisticas_1_para_2[app_name] = dict()

					# guarda nº de linhas do arquivo
					num_linhas_do_arquivo = get_numero_linhas_do_arquivo(file_full_name)
					if num_linhas_do_arquivo is None:
						arquivos_com_erro_ao_analisar.append(file_relative_name)
						# pula o arquivo se houve erro anterior ao analisar
						continue
					else:
						estatisticas_1_para_2[app_name][file_relative_name] = {
							'num_linhas': num_linhas_do_arquivo,
							'alterado': False,
							'excluido': False,
							'num_linhas_incluidas': 0,
							'num_linhas_excluidas': 0,
							'num_linhas_alteradas': 0,
						}

					# o arquivo existe no projeto 2?
					if not existe_este_arquivo(ANOTHER_FILE_PATH, file_relative_name):
						estatisticas_1_para_2[app_name][file_relative_name]['excluido'] = True

					else:
						# o arquivo é igual ao do projeto 2?
						if arquivo_1_eh_igual_arquivo_2(FILE_PATH, file_relative_name, ANOTHER_FILE_PATH, file_relative_name):
							continue # passa o próximo arquivo

						else:
							estatisticas_1_para_2[app_name][file_relative_name]['alterado'] = True
							estatisticas_diff = get_diff_stats(FILE_PATH+file_relative_name, ANOTHER_FILE_PATH+file_relative_name)

							if estatisticas_diff:
								estatisticas_1_para_2[app_name][file_relative_name]['num_linhas_incluidas'] = estatisticas_diff.get('adicionadas')
								estatisticas_1_para_2[app_name][file_relative_name]['num_linhas_excluidas'] = estatisticas_diff.get('removidas')
								estatisticas_1_para_2[app_name][file_relative_name]['num_linhas_alteradas'] = estatisticas_diff.get('modificadas')

			dados = estatisticas_1_para_2
			estatisticas_show = gerar_estatisticas_pie_show(dados)
			estatisticas_impacto_show = gerar_estatisticas_impacto_show(dados)

			subtitle = 'Resultados de execução'

			return render(request, 'gerar_estatisticas_pie_show.html', {
				'graphic1': estatisticas_show.get('graphic1'),
				'graphic2': estatisticas_show.get('graphic2'),
				'tabela_dados': estatisticas_show.get('tabela_dados'),
				'total_modificacoes': estatisticas_show.get('total_modificacoes'),
				'total_linhas': estatisticas_show.get('total_linhas'),
				'graphic3': estatisticas_impacto_show.get('graphic1'),
        		'graphic4': estatisticas_impacto_show.get('graphic2'),
        		'tabela_dados2': estatisticas_impacto_show.get('tabela_dados'),
			})

		else:
			messages.error(request, 'Necessário informar configuração para execução da ferramenta')
			return render(request, 'index.html', {'title': 'Forkuptool', 'subtitle': 'Bem-vindo', })


			### Repositório 2 para o 1: merge-ifrn-xxx para a master IFSULDEMINAS
			''' 
				Objetivos:
				- verificar quantos arquivos no merge-ifrn-xxx foram INCLUÍDOS com relação à master (não existem na master)
				- contabilizar por MÓDULO (app)
			'''
			# FILE_PATH = configuracao_obj.path_repositorio_vendor
			# ANOTHER_FILE_PATH = configuracao_obj.path_repositorio_client


def gerar_estatisticas_impacto_show(dados):
	# Processamento: calcular % de modificação por app
	apps_stats = {}
	for app, arquivos in dados.items():
		linhas_modificadas = 0
		linhas_totais = 0

		for arquivo, stats in arquivos.items():
			linhas_modificadas += (
				stats.get('num_linhas_incluidas', 0) +
				stats.get('num_linhas_excluidas', 0) +
				stats.get('num_linhas_alteradas', 0)
			)
			linhas_totais += stats.get('num_linhas', 0)

		# Novo cálculo: % de modificação em relação ao tamanho do app
		percentual_impacto = (linhas_modificadas / linhas_totais * 100) if linhas_totais > 0 else 0

		apps_stats[app] = {
			'linhas_modificadas': linhas_modificadas,
			'linhas_totais': linhas_totais,
			'percentual_impacto': percentual_impacto
		}

	# Ordenar apps por % de impacto (top 15)
	top_apps = sorted(apps_stats.items(), key=lambda x: x[1]['percentual_impacto'], reverse=True)[:15]

	# Dados para gráficos
	labels = [app[0] for app in top_apps]
	percentuais = [app[1]['percentual_impacto'] for app in top_apps]
	linhas_mod = [app[1]['linhas_modificadas'] for app in top_apps]

	# Gráfico 1: % de Impacto por App (Barras Horizontais)
	plt.figure(figsize=(10, 6))
	sns.barplot(x=percentuais, y=labels, palette="viridis")
	plt.title('Top 15 Apps por % de Modificação (Impacto Relativo)')
	plt.xlabel('% do App Modificado')
	plt.ylabel('Aplicação')

	buffer1 = BytesIO()
	plt.savefig(buffer1, format='png', bbox_inches='tight')
	plt.close()
	graphic1 = base64.b64encode(buffer1.getvalue()).decode('utf-8')

	# Gráfico 2: Comparação Modificações Absolutas x Impacto Relativo (Scatter Plot)
	plt.figure(figsize=(10, 6))
	plt.scatter(
		x=[app[1]['linhas_modificadas'] for app in top_apps],
		y=percentuais,
		s=100,  # Tamanho dos pontos
		c=percentuais,  # Cor por % de impacto
		cmap='coolwarm'
	)
	plt.title('Relação: Linhas Modificadas (Absoluto) vs % de Impacto (Relativo)')
	plt.xlabel('Linhas Modificadas (Absoluto)')
	plt.ylabel('% de Impacto (Relativo)')
	plt.colorbar(label='% de Impacto')

	# Adicionar rótulos dos apps
	for i, app in enumerate(labels):
		plt.annotate(app, (linhas_mod[i], percentuais[i]), textcoords="offset points", xytext=(0,5), ha='center')

	buffer2 = BytesIO()
	plt.savefig(buffer2, format='png', bbox_inches='tight')
	plt.close()
	graphic2 = base64.b64encode(buffer2.getvalue()).decode('utf-8')

	# Tabela de dados
	tabela_dados = []
	for i, (app, stats) in enumerate(top_apps, 1):
		tabela_dados.append({
			'posicao': i,
			'app': app,
			'linhas_totais': stats['linhas_totais'],
			'linhas_modificadas': stats['linhas_modificadas'],
			'percentual_impacto': f"{stats['percentual_impacto']:.1f}%",
			'impacto_normalizado': stats['percentual_impacto'] / 100  # Para uso em estilização
		})

	return {
        'graphic1': graphic1,
        'graphic2': graphic2,
        'tabela_dados': tabela_dados,
    }


def gerar_estatisticas_pie_show(dados):
	# Processar os dados para calcular totais por app
	apps_stats = {}
	for app, arquivos in dados.items():
		modificacoes = 0
		linhas_modificadas = 0
		linhas_totais = 0

		for arquivo, stats in arquivos.items():
			if stats.get('alterado') or stats.get('excluido'):
				modificacoes += 1

			linhas_modificadas += (stats.get('num_linhas_incluidas', 0) + \
								stats.get('num_linhas_excluidas', 0) + \
								stats.get('num_linhas_alteradas', 0))

			if not stats.get('excluido', False):
				linhas_totais += stats.get('num_linhas', 0)

		apps_stats[app] = {
			'modificacoes': modificacoes,
			'linhas_modificadas': linhas_modificadas,
			'linhas_totais': linhas_totais
		}


	# Ordenar apps por modificações (top 15)
	top_apps = sorted(apps_stats.items(), 
					key=lambda x: x[1]['modificacoes'], 
					reverse=True)[:15]

	# Preparar dados para gráficos
	labels = [app[0] for app in top_apps]
	mod_values = [app[1]['modificacoes'] for app in top_apps]
	linhas_values = [app[1]['linhas_modificadas'] for app in top_apps]

	# Gráfico 1: Modificações por App
	plt.figure(figsize=(10, 8))
	plt.pie(
		mod_values, 
		labels=labels, 
		autopct='%1.1f%%',
		startangle=90, 
		colors=sns.color_palette('pastel')
	)
	plt.title('Top 15 Apps por Número de Modificações')

	buffer1 = BytesIO()
	plt.savefig(buffer1, format='png', bbox_inches='tight')
	plt.close()
	graphic1 = base64.b64encode(buffer1.getvalue()).decode('utf-8')

	# Gráfico 2: Linhas Modificadas por App
	plt.figure(figsize=(10, 8))
	plt.pie(
		linhas_values, 
		labels=labels, 
		autopct='%1.1f%%',
		startangle=90, 
		colors=sns.color_palette('Set2')
	)
	plt.title('Top 15 Apps por Linhas Modificadas')

	buffer2 = BytesIO()
	plt.savefig(buffer2, format='png', bbox_inches='tight')
	plt.close()
	graphic2 = base64.b64encode(buffer2.getvalue()).decode('utf-8')

	# Preparar dados para tabela
	tabela_dados = []
	for i, (app, stats) in enumerate(top_apps, 1):
		tabela_dados.append({
			'posicao': i,
			'app': app,
			'modificacoes': stats['modificacoes'],
			'linhas_modificadas': stats['linhas_modificadas'],
			'percentual_mod': f"{(stats['modificacoes']/sum(mod_values)*100):.1f}%",
			'percentual_linhas': f"{(stats['linhas_modificadas']/sum(linhas_values)*100):.1f}%"
		})


	return {
        'graphic1': graphic1,
        'graphic2': graphic2,
        'tabela_dados': tabela_dados,
        'total_modificacoes': sum(mod_values),
        'total_linhas': sum(linhas_values)
    }