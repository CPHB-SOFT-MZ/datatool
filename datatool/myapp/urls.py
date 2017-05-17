# -*- coding: utf-8 -*-
from django.conf.urls import url
from datatool.myapp.views import *

urlpatterns = [
    url(r'^list/$', list, name='list'),
    url(r'^remove/(?P<file_name>.\S+)$', remove, name='remove'),
    url(r'^analyze/$', analyze, name='analyze'),
    url(r'^analyze-data/$', analyze_data, name='analyze-data')
]
