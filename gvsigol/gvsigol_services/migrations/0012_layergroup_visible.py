# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-05-24 11:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gvsigol_services', '0011_auto_20180413_0657'),
    ]

    operations = [
        migrations.AddField(
            model_name='layergroup',
            name='visible',
            field=models.BooleanField(default=False),
        ),
    ]
