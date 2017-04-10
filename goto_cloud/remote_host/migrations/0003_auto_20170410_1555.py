# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-10 15:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('remote_host', '0002_auto_20170407_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remotehost',
            name='os',
            field=models.CharField(choices=[('DEBIAN', 'Debian'), ('LINUX', 'Linux'), ('UBUNTU', 'Ubuntu'), ('WINDOWS', 'Windows')], default='Debian', max_length=255),
        ),
    ]
