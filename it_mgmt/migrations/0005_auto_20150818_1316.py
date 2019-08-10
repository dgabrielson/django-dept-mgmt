# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("it_mgmt", "0004_computer_host_id")]

    operations = [
        migrations.AlterField(
            model_name="computer",
            name="host_id",
            field=models.SlugField(max_length=256, blank=True),
        )
    ]
