# -*- coding: utf-8 -*-
from django.conf.urls import url
from datatool.myapp.views import list, remove

urlpatterns = [
    url(r'^list/$', list, name='list'),
    url(r'^remove/(?P<file_name>.\S+)$', remove, name='remove')
]
