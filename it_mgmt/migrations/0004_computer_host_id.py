# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("it_mgmt", "0003_auto_20150611_1529")]

    operations = [
        migrations.AddField(
            model_name="computer",
            name="host_id",
            field=models.CharField(max_length=256, blank=True),
        )
    ]
