# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-11-05 22:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0004_contrato_coste'),
    ]

    operations = [
        migrations.AddField(
            model_name='contrato',
            name='user',
            field=models.CharField(default='', max_length=20),
        ),
    ]