# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-03-05 23:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sbehost', '0012_auto_20170305_2228'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gameservice',
            name='game_host',
        ),
    ]
