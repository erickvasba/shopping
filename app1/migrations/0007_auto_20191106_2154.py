# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-11-06 21:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0006_remove_contrato_dueno'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contrato',
            name='final',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='contrato',
            name='inicio',
            field=models.DateField(),
        ),
    ]
