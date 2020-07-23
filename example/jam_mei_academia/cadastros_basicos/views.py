from django.http import HttpResponse
from django.shortcuts import render

def index(request):
	#return HttpResponse("Teste de configuração da aplicação - apostila página 57.")
	return render(request,"admin/base.html")
