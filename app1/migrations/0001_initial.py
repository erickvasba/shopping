# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-07-30 20:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matricula', models.CharField(max_length=10)),
                ('dueno', models.CharField(max_length=50)),
                ('fecha', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pagos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pago', models.CharField(max_length=10)),
                ('fecha', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Parking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matricula', models.CharField(max_length=10)),
                ('user', models.CharField(max_length=10)),
                ('fecha_ingreso', models.DateTimeField(null=True)),
                ('fecha_salida', models.DateTimeField(blank=True, null=True)),
                ('abierto', models.BooleanField(default=True)),
                ('fecha', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vitacora',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=10)),
                ('matricula', models.CharField(max_length=10)),
                ('obs', models.CharField(max_length=100)),
                ('fecha', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='pagos',
            name='matricula',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app1.Parking'),
        ),
    ]
