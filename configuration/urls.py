from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^modulo_configuration/', views.index, name='modulo_configuration'),
]