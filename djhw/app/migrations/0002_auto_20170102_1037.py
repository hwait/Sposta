# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-02 04:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='duration',
            field=models.FloatField(null=True),
        ),
    ]