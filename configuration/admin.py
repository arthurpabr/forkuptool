from django.contrib import admin

from .models import ConfiguracaoGeral, ConfiguracaoFerramenta, ArquivosComparados


@admin.register(ConfiguracaoGeral)
class ConfiguracaoGeralAdmin(admin.ModelAdmin):
   ordering = ('id',)


@admin.register(ConfiguracaoFerramenta)
class ConfiguracaoFerramentaAdmin(admin.ModelAdmin):
   ordering = ('id',)



@admin.register(ArquivosComparados)
class ArquivosComparadosAdmin(admin.ModelAdmin):
	ordering = ('-comparacao__datahorario_execucao',)
	list_filter = ('comparacao','arquivo_vendor__igual_ao_client')

	def has_add_permission(self, request):
		return False

	def has_delete_permission(self, request, obj=None):
		return False