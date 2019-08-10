# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("places", "0001_initial"),
        ("office_mgmt", "0001_initial"),
        ("people", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Computer",
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
                ("common_name", models.CharField(max_length=64)),
                ("hardware", models.CharField(max_length=256)),
                (
                    "operating_system",
                    models.CharField(max_length=64, null=True, blank=True),
                ),
                ("processor", models.CharField(max_length=64, null=True, blank=True)),
                ("ram", models.CharField(max_length=32, null=True, blank=True)),
                ("harddrive", models.CharField(max_length=32, null=True, blank=True)),
                (
                    "manufacturing_year",
                    models.PositiveSmallIntegerField(null=True, blank=True),
                ),
                ("admin_user", models.CharField(max_length=32, null=True, blank=True)),
                (
                    "admin_password",
                    models.CharField(max_length=32, null=True, blank=True),
                ),
                (
                    "ssh_port",
                    models.PositiveSmallIntegerField(
                        default=22, null=True, verbose_name="SSH Port", blank=True
                    ),
                ),
                ("notes", models.TextField(null=True, blank=True)),
                (
                    "asset",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        blank=True,
                        to="office_mgmt.Asset",
                        null=True,
                    ),
                ),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ComputerFlag",
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
                ("slug", models.SlugField(unique=True, max_length=64)),
                ("verbose_name", models.CharField(max_length=64)),
            ],
            options={"ordering": ["verbose_name"]},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ComputerKey",
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
                    "key",
                    models.CharField(
                        default="", max_length=255, db_index=True, blank=True
                    ),
                ),
                (
                    "computer",
                    models.OneToOneField(
                        on_delete=models.deletion.CASCADE,
                        related_name="api_key",
                        to="it_mgmt.Computer",
                    ),
                ),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IPAddress",
            fields=[
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
                ("number", models.IPAddressField(serialize=False, primary_key=True)),
                ("hostname", models.CharField(max_length=64)),
                ("aliases", models.CharField(max_length=256, null=True, blank=True)),
                ("in_use", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "IP Address",
                "verbose_name_plural": "IP Addresses",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Licence",
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
                ("value", models.TextField()),
                (
                    "computer",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to="it_mgmt.Computer",
                        null=True,
                    ),
                ),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="NetworkInterface",
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
                ("name", models.CharField(max_length=64)),
                ("primary", models.BooleanField(default=True)),
                (
                    "type",
                    models.CharField(
                        max_length=2,
                        choices=[
                            (b"e", b"Ethernet"),
                            (b"w", b"Wifi"),
                            (b"b", b"Bluetooth"),
                        ],
                    ),
                ),
                (
                    "mac_address",
                    models.CharField(max_length=104, verbose_name="MAC Address"),
                ),
                (
                    "computer",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="it_mgmt.Computer"
                    ),
                ),
                (
                    "ip_address",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        verbose_name="IP Address",
                        blank=True,
                        to="it_mgmt.IPAddress",
                        null=True,
                    ),
                ),
            ],
            options={"ordering": ("-primary", "name")},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Status",
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
                ("value", models.TextField()),
                (
                    "computer",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="it_mgmt.Computer"
                    ),
                ),
            ],
            options={"get_latest_by": "created"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="StatusKey",
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
                ("slug", models.SlugField(max_length=64)),
                ("verbose_name", models.CharField(max_length=64)),
                (
                    "volatile",
                    models.BooleanField(
                        default=False,
                        help_text="This should be set if the associated status values change frequently",
                    ),
                ),
                (
                    "data_type",
                    models.CharField(
                        default="r",
                        max_length=2,
                        choices=[
                            (b"r", b"raw"),
                            (b"dt", b"datetime"),
                            (b"du", b"disk usage"),
                            (b"i", b"int"),
                            (b"f", b"float"),
                            (b"m", b"memory"),
                            (b"p", b"percentage"),
                        ],
                    ),
                ),
            ],
            options={"ordering": ["verbose_name"]},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="WorkNote",
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
                ("value", models.TextField()),
                (
                    "computer",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to="it_mgmt.Computer",
                        null=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={"ordering": ["-created"]},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="status",
            name="key",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE, to="it_mgmt.StatusKey"
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="networkinterface", unique_together=set([("computer", "name")])
        ),
        migrations.AddField(
            model_name="computer",
            name="flags",
            field=models.ManyToManyField(to="it_mgmt.ComputerFlag", blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="computer",
            name="person",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                blank=True,
                to="people.Person",
                help_text='Only people with the "asset-owner" flag are shown',
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="computer",
            name="room",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                blank=True,
                to="places.Room",
                null=True,
            ),
            preserve_default=True,
        ),
    ]
