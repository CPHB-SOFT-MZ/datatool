# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-10 07:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_auto_20170510_0715'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='filename',
            new_name='file_name',
        ),
    ]
