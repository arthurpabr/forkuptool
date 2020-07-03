from django.shortcuts import render

def index(request):
    return render(request, 'configuration.html', {'title': 'Forkuptool',
    	'subtitle': 'Módulo de configuração', 'messages': None, })

