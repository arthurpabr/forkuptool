from django.contrib import admin

from .models import Modalidade, Periodicidade, Promocao, OfertaDeTurma, \
	Professor, Turma, Recepcionista


@admin.register(Recepcionista)
class RecepcionistaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    ordering = ('nome',)

