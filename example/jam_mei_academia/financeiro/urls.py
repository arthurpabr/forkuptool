from django.conf.urls import url

from . import models

urlpatterns = [
	url(r'^mensalidades_em_atraso/', models.buscar_mensalidades_em_atraso, name='mensalidades_em_atraso'),
	url(r'^mensalidades_recebidas/', models.buscar_mensalidades_recebidas, name='mensalidades_recebidas'),
	url(r'^calcular_mensalidades/', models.calcular_mensalidades, name='calcular_mensalidades'),
]