from django.contrib import admin
from .models import Mensalidade

@admin.register(Mensalidade)
class MensalidadeAdmin(admin.ModelAdmin):
    list_display = ('ano_referencia','mes_referencia','matricula','situacao')
    ordering = ('-ano_referencia','-mes_referencia','matricula__aluno__nome','situacao')
    list_filter = ('ano_referencia', 'mes_referencia','matricula','situacao')
    search_fields = ('matricula__aluno__nome',)
