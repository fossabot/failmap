# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-27 13:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0012_auto_20170927_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='url',
            name='organizations',
            field=models.ManyToManyField(related_name='u_many_o_upgrade', to='organizations.Organization'),
        ),
    ]