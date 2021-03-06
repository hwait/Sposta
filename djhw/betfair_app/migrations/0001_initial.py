# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-27 08:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BFChamp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mcid', models.IntegerField(null=True)),
                ('bfid', models.IntegerField()),
                ('lid', models.IntegerField(db_index=True, null=True)),
                ('sport', models.IntegerField(null=True)),
                ('country_code', models.CharField(max_length=2, null=True)),
                ('name', models.CharField(max_length=100, null=True)),
                ('gender', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BFEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meid', models.IntegerField(null=True)),
                ('bfid', models.IntegerField()),
                ('lid', models.IntegerField(db_index=True, null=True)),
                ('rid1', models.IntegerField(null=True)),
                ('rid2', models.IntegerField(null=True)),
                ('dt', models.DateTimeField(db_index=True, null=True)),
                ('dtc', models.DateTimeField(db_index=True, null=True)),
                ('dtip', models.DateTimeField(null=True)),
                ('status', models.IntegerField(null=True)),
                ('reversed', models.IntegerField(null=True)),
                ('cid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='betfair_app.BFChamp')),
            ],
        ),
        migrations.CreateModel(
            name='BFOdds',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('b1odds', models.FloatField()),
                ('b2odds', models.FloatField()),
                ('b1size', models.FloatField(null=True)),
                ('b2size', models.FloatField(null=True)),
                ('l1odds', models.FloatField()),
                ('l2odds', models.FloatField()),
                ('l1size', models.FloatField(null=True)),
                ('l2size', models.FloatField(null=True)),
                ('dtc', models.DateTimeField(db_index=True, null=True)),
                ('ip', models.NullBooleanField()),
                ('eid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='betfair_app.BFEvent')),
            ],
        ),
        migrations.CreateModel(
            name='BFPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mpid', models.IntegerField(null=True)),
                ('lid', models.IntegerField(db_index=True, null=True)),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('gender', models.IntegerField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='bfevent',
            name='pid1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player1', to='betfair_app.BFPlayer'),
        ),
        migrations.AddField(
            model_name='bfevent',
            name='pid2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player2', to='betfair_app.BFPlayer'),
        ),
    ]
