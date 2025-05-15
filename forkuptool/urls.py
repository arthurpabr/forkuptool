from django.conf.urls import include
from django.contrib import admin
from django.urls import path

admin.site.site_header = 'Forkuptool'
admin.site.site_title = 'Forkuptool'
admin.site.index_title = 'Forkuptool'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('analyze.urls')),
    path('', include('configuration.urls')),
    path('', include('execution.urls')),
    path('', include('gen_statistics.urls')),
]
