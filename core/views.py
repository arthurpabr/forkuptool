from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {'title': 'Forkuptool',
    	'subtitle': 'Bem-vindo', 'messages': None, })

