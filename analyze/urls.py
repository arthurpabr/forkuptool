from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
	url(r'^modulo_analyze/', views.index, name='modulo_analyze'),
	url(r'^info_criacao_client/', views.info_criacao_client, name='info_criacao_client'),
	url(r'^analisar_timeline/', views.analisar_timeline, name='analisar_timeline'),
	url(r'^simular_conflitos/', views.simular_conflitos, name='simular_conflitos'),
    url(r'^simular_conflitos_xls/(?P<configuracaoferramenta_escolhida>\d+)/(?P<nome_branch_origem>\w+)/(?P<nome_branch_forkeado>\w+)/(?P<apagar_branch_merge>\w+)$', views.simular_conflitos_xls, name='simular_conflitos_xls'),
	url(r'^comparar_repositorios/', views.comparar_repositorios, name='comparar_repositorios'),
	url(r'^check_thread/(?P<id>[0-9]+)/?$',views.check_thread_task, name='check_thread_task'),
	url(r'^visualizar_comparacao_repositorios/', views.visualizar_comparacao_repositorios, name='visualizar_comparacao_repositorios'),
	url(r'^visualizar_comparacao_repositorios/(?P<id>[0-9]+)/?$', views.visualizar_comparacao_repositorios, name='visualizar_comparacao_repositorios'),
	url(r'^visualizar_analise_diferencas/(?P<id>[0-9]+)/?$',views.visualizar_analise_diferencas, name='visualizar_analise_diferencas'),	
	url(r'^visualizar_diff_entre_arquivos/(?P<id>[0-9]+)/?$',views.visualizar_diff_entre_arquivos, name='diff_entre_arquivos'),	
	url(r'^diff/', TemplateView.as_view(template_name='diff.html'), name='diff'),
]