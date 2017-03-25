# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-03-25 04:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sbehost', '0014_auto_20170323_0122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameservice',
            name='application',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sbehost.ServiceApplication'),
        ),
        migrations.AlterField(
            model_name='gameservice',
            name='game_host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sbehost.GameHost'),
        ),
        migrations.AlterField(
            model_name='gameservice',
            name='status',
            field=models.CharField(choices=[(b'1', b'success'), (b'2', b'reset'), (b'3', b'timeout')], default=b'1', max_length=16, verbose_name=b'Service Status'),
        ),
    ]
