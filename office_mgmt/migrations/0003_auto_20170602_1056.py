# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-02 15:56
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("office_mgmt", "0002_auto_20150611_1529")]

    operations = [
        migrations.AlterModelOptions(
            name="asset",
            options={"base_manager_name": "objects", "ordering": ["-created"]},
        ),
        migrations.AlterModelOptions(
            name="loangroup", options={"base_manager_name": "objects"}
        ),
        migrations.AlterModelOptions(
            name="loanitem", options={"base_manager_name": "objects"}
        ),
        migrations.AlterModelOptions(
            name="loanrecord",
            options={
                "base_manager_name": "objects",
                "get_latest_by": "loaned_dt",
                "ordering": ["-loaned_dt"],
            },
        ),
        migrations.AlterModelOptions(
            name="paperwork",
            options={
                "base_manager_name": "objects",
                "verbose_name_plural": "paperwork",
            },
        ),
        migrations.AlterField(
            model_name="asset",
            name="person",
            field=models.ForeignKey(
                blank=True,
                help_text='Only people with the "asset-owner" flag are shown',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="people.Person",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="room",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="places.Room",
            ),
        ),
    ]