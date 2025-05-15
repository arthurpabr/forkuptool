from django.urls import path
from . import views

urlpatterns = [
	path('modulo_configuration/', views.index, name='modulo_configuration'),
]