from django.urls import path
from . import views

urlpatterns = [
	path('modulo_statistics/', views.index, name='modulo_statistics'),
	path('gerar_estatisticas/', views.gerar_estatisticas, name='gerar_estatisticas'),
]