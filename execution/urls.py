from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^modulo_execution/', views.index, name='modulo_execution'),
	url(r'^executar_ferramenta/', views.executar_ferramenta, name='executar_ferramenta'),
]