# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-11-06 22:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0007_auto_20191106_2154'),
    ]

    operations = [
        migrations.AddField(
            model_name='contrato',
            name='fecha',
            field=models.DateField(auto_now=True),
        ),
    ]
