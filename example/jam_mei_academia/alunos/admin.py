from django.contrib import admin
from .models import Aluno, Matricula
from financeiro.models import Mensalidade

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome','sexo','numero_celular','nome_do_responsavel',)
    ordering = ('nome',)
    list_filter = ('nome', 'sexo')
    search_fields = ('nome',)


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aluno','turma','valor_da_mensalidade','dia_de_vencimento','situacao_matricula',\
        'mensalidades_em_atraso',)
    ordering = ('aluno__nome',)
    list_filter = ('turma', 'situacao_matricula')
    search_fields = ('aluno__nome',)

    def mensalidades_em_atraso(self, obj):
    	str_retorno = ''
    	mensalidades_em_atraso = []
    	mensalidades_em_atraso = Mensalidade.objects.filter(matricula=obj,situacao=Mensalidade.SITUACAO_PENDENTE)
    	if mensalidades_em_atraso:
    		for mensalidade in mensalidades_em_atraso:
    			str_retorno += str(mensalidade.get_str_mes_ano())+' '
    	else:
    		str_retorno = 'não há'

    	return str_retorno

