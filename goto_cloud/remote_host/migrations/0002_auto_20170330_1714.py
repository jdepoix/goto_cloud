# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-30 17:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('remote_host', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remotehost',
            name='version',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
