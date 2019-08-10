# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("it_mgmt", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="ClientIdentifier",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="last modification time"
                    ),
                ),
                ("key", models.SlugField()),
                ("value", models.CharField(max_length=128)),
                (
                    "computer",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="it_mgmt.Computer"
                    ),
                ),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        )
    ]
