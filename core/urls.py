from django.urls import path
from . import views

urlpatterns = [
	path('index/', views.index, name='index'),
	path('index/', views.index, name='home'),
	path('', views.index, name='index'),
]