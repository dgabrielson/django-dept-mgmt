# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("office_mgmt", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="loangroup",
            name="flag",
            field=models.OneToOneField(
                on_delete=models.deletion.CASCADE,
                to="people.PersonFlag",
                help_text="The person flag corresponding to this group",
            ),
        )
    ]
