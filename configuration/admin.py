from django.contrib import admin

from .models import ConfiguracaoGeral, ConfiguracaoFerramenta


@admin.register(ConfiguracaoGeral)
class ConfiguracaoGeralAdmin(admin.ModelAdmin):
   ordering = ('id',)


@admin.register(ConfiguracaoFerramenta)
class ConfiguracaoFerramentaAdmin(admin.ModelAdmin):
   ordering = ('id',)