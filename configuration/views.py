from django.shortcuts import render

def index(request):
    return render(request, 'configuration.html', {'title': 'Forkuptool - Módulo de configuração',
    	'subtitle': 'Configurações gerais do sistema', 'messages': None, })

