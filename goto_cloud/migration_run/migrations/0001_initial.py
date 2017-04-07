# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-06 13:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('migration_plan', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MigrationRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='migration_runs', to='migration_plan.MigrationPlan')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
