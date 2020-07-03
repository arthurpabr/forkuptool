from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^modulo_analyze/', views.index, name='modulo_analyze'),
	url(r'^info_criacao_client/', views.info_criacao_client, name='info_criacao_client'),
	url(r'^analisar_timeline/', views.analisar_timeline, name='analisar_timeline'),
]