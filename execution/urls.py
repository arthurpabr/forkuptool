from django.urls import path
from . import views

urlpatterns = [
	path('modulo_execution/', views.index, name='modulo_execution'),
	path('executar_ferramenta/', views.executar_ferramenta, name='executar_ferramenta'),
]