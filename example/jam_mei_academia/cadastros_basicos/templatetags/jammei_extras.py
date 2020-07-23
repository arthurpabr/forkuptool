from django import template

register = template.Library()

@register.filter
def retira_adm(value):
    return value.replace("administração","")