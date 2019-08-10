# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("it_mgmt", "0002_clientidentifier")]

    operations = [
        migrations.AlterField(
            model_name="ipaddress",
            name="number",
            field=models.GenericIPAddressField(serialize=False, primary_key=True),
        )
    ]
