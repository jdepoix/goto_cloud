# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-12 14:00
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('target', '0001_initial'),
        ('remote_host', '0001_initial'),
        ('migration_run', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(max_length=255)),
                ('system_info', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('migration_run', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sources', to='migration_run.MigrationRun')),
                ('remote_host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sources', to='remote_host.RemoteHost')),
                ('target', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='source', to='target.Target')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
