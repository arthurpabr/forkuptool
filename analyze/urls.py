from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
	path('modulo_analyze/', views.index, name='modulo_analyze'),
	path('info_criacao_client/', views.info_criacao_client, name='info_criacao_client'),
	path('analisar_timeline/', views.analisar_timeline, name='analisar_timeline'),
	path('simular_conflitos/', views.simular_conflitos, name='simular_conflitos'),
    path('simular_conflitos_xls/<int:configuracaoferramenta_escolhida>/<str:nome_branch_origem>/<str:nome_branch_forkeado>/<str:apagar_branch_merge>', views.simular_conflitos_xls, name='simular_conflitos_xls'),
	path('comparar_repositorios/', views.comparar_repositorios, name='comparar_repositorios'),
	path('check_thread/<int:id>/',views.check_thread_task, name='check_thread_task'),
	path('visualizar_comparacao_repositorios/', views.visualizar_comparacao_repositorios, name='visualizar_comparacao_repositorios'),
	path('visualizar_comparacao_repositorios/<int:id>/', views.visualizar_comparacao_repositorios, name='visualizar_comparacao_repositorios'),
	path('visualizar_analise_diferencas/<int:id>/',views.visualizar_analise_diferencas, name='visualizar_analise_diferencas'),	
	path('visualizar_diff_entre_arquivos/<int:id>/',views.visualizar_diff_entre_arquivos, name='diff_entre_arquivos'),	
	path('diff/', TemplateView.as_view(template_name='diff.html'), name='diff'),
]