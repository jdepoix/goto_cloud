# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-12 14:00
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('remote_host', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('blueprint', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('remote_host', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='targets', to='remote_host.RemoteHost')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
