from django.contrib import admin

from .models import Modalidade, Periodicidade, Promocao, OfertaDeTurma, \
	Professor, Turma

@admin.register(Modalidade)
class ModalidadeAdmin(admin.ModelAdmin):
    list_display = ('descricao',)
    ordering = ('descricao',)

@admin.register(Periodicidade)
class PeriodicidadeAdmin(admin.ModelAdmin):
    list_display = ('descricao',)
    ordering = ('descricao',)

@admin.register(Promocao)
class PromocaoAdmin(admin.ModelAdmin):
    list_display = ('descricao',)
    ordering = ('descricao',)

@admin.register(OfertaDeTurma)
class OfertaDeTurmaAdmin(admin.ModelAdmin):
    list_display = ('modalidade','periodicidade','promocao','valor_da_mensalidade',)
    ordering = ('modalidade','periodicidade','promocao',)
    list_filter = ('modalidade', 'promocao')

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    ordering = ('nome',)

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('horario','dias_de_aula','modalidade','tipo_turma', 'professor',)
    ordering = ('horario',)
    list_filter = ('modalidade', 'professor')
    search_fields = ('modalidade__descricao','professor__nome',)