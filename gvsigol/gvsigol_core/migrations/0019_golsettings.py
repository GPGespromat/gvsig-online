# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-11-15 14:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gvsigol_core', '0018_project_restricted_extent'),
    ]

    operations = [
        migrations.CreateModel(
            name='GolSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plugin_name', models.TextField()),
                ('key', models.TextField()),
                ('value', models.TextField()),
            ],
        ),
    ]
