# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("it_mgmt", "0005_auto_20150818_1316")]

    operations = [
        migrations.AddField(
            model_name="networkinterface",
            name="managed",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="networkinterface",
            name="type",
            field=models.CharField(
                max_length=2,
                choices=[
                    (b"e", b"Ethernet"),
                    (b"w", b"Wi-Fi"),
                    (b"b", b"Bluetooth"),
                    (b"t", b"Thunderbolt"),
                ],
            ),
        ),
    ]
