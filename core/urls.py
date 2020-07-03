from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^index/', views.index, name='index'),
	url(r'^index/', views.index, name='home'),
	url(r'^$', views.index, name='index'),
]