# -*- coding: utf-8 -*-
from django.db import models


class Document(models.Model):
    # TODO: Append the date to the filename
    docfile = models.FileField(upload_to='documents')
    file_name = models.CharField(max_length=255, default=None)
