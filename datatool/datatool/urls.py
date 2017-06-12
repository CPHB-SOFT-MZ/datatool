from django.conf.urls import url
from datatool.datatool.views import *

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^remove/(?P<file_name>.\S+)$', remove, name='remove'),
    url(r'^analyze/$', analyze, name='analyze'),
    url(r'^analyze-data/$', analyze_data, name='analyze-data')
]
