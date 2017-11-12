# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-12 11:49
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0019_promise'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promise',
            name='created_on',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True),
        ),
        migrations.AlterField(
            model_name='promise',
            name='expires_on',
            field=models.DateTimeField(blank=True, help_text='When in the future this promise is expected to be fulfilled.', null=True),
        ),
        migrations.AlterField(
            model_name='promise',
            name='notes',
            field=models.TextField(blank=True, help_text='Context information about the promise (eg: ticket reference).', null=True),
        ),
    ]
