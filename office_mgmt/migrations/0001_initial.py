# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("places", "0001_initial"), ("people", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Asset",
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
                ("description", models.CharField(max_length=256)),
                (
                    "status",
                    models.CharField(
                        default="u",
                        max_length=3,
                        choices=[
                            (b"u", b"In use"),
                            (b"i", b"Inactive"),
                            (b"p", b"Do paperwork"),
                            (b"dw", b"Disposed (awaiting pickup)"),
                            (b"dg", b"Disposed (gone)"),
                            (b"sa", b"For sale"),
                            (b"sw", b"Sold (awaiting pickup)"),
                            (b"sg", b"Sold (gone)"),
                        ],
                    ),
                ),
                ("serial_number", models.CharField(max_length=64)),
                ("property_number", models.IntegerField(null=True, blank=True)),
                (
                    "security_id",
                    models.CharField(
                        max_length=128, verbose_name="Security ID", blank=True
                    ),
                ),
                ("date_acquired", models.DateField(null=True, blank=True)),
                ("purchase_order_number", models.CharField(max_length=32, blank=True)),
                ("original_cost", models.CharField(max_length=32, blank=True)),
                (
                    "original_fopal",
                    models.CharField(
                        max_length=64, verbose_name="Original FOPAL", blank=True
                    ),
                ),
                (
                    "current_condition",
                    models.CharField(
                        blank=True,
                        max_length=2,
                        null=True,
                        choices=[
                            (b"A", b"Excellent (like new)"),
                            (b"B", b"Good (working)"),
                            (b"C", b"Poor (needs repair)"),
                            (b"D", b"Not Working"),
                            (b"9", b"Stolen"),
                            (b"0", b"Missing"),
                        ],
                    ),
                ),
                ("off_site", models.BooleanField(default=False)),
                ("reserve_bid", models.CharField(max_length=32, blank=True)),
                ("sale_amount", models.CharField(max_length=32, blank=True)),
                ("date_disposed", models.DateField(null=True, blank=True)),
                ("notes", models.TextField(null=True, blank=True)),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        blank=True,
                        to="people.Person",
                        help_text='Only people with the "asset-owner" flag are shown',
                        null=True,
                    ),
                ),
                (
                    "room",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        blank=True,
                        to="places.Room",
                        null=True,
                    ),
                ),
            ],
            options={"ordering": ["-created"]},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="LoanGroup",
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
                (
                    "flag",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to="people.PersonFlag",
                        help_text="The person flag corresponding to this group",
                        unique=True,
                    ),
                ),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="LoanItem",
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
                (
                    "tag",
                    models.CharField(
                        help_text="A short description of the item, possibly a serial number or sticker ID",
                        max_length=128,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="A longer description of the item", blank=True
                    ),
                ),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="LoanRecord",
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
                (
                    "loaned_dt",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="Loaned"
                    ),
                ),
                (
                    "returned_dt",
                    models.DateTimeField(
                        null=True, verbose_name="Returned", blank=True
                    ),
                ),
                (
                    "loan_type",
                    models.CharField(
                        default="s",
                        max_length=2,
                        choices=[(b"s", b"Short term"), (b"l", b"Long term")],
                    ),
                ),
                (
                    "deposit",
                    models.CharField(
                        default="",
                        help_text="Amount of deposit taken, if any",
                        max_length=8,
                        blank=True,
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="office_mgmt.LoanItem"
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="people.Person"
                    ),
                ),
            ],
            options={"ordering": ["-loaned_dt"], "get_latest_by": "loaned_dt"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Paperwork",
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
                ("description", models.CharField(max_length=256)),
                ("attachment", models.FileField(upload_to="asset-paperwork/%Y/%m")),
                (
                    "asset",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to="office_mgmt.Asset",
                        null=True,
                    ),
                ),
            ],
            options={"verbose_name_plural": "Paperwork"},
            bases=(models.Model,),
        ),
    ]
