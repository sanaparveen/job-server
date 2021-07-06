# Generated by Django 3.2.4 on 2021-07-06 08:59

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0052_alter_user_managers"),
    ]

    operations = [
        migrations.RenameField(
            model_name="release",
            old_name="publishing_user",
            new_name="created_by",
        ),
        migrations.RemoveField(
            model_name="release",
            name="files",
        ),
        migrations.RemoveField(
            model_name="release",
            name="published_at",
        ),
        migrations.AddField(
            model_name="release",
            name="created_at",
            field=models.DateTimeField(default=datetime.datetime.utcnow),
        ),
        migrations.CreateModel(
            name="ReleaseFile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.TextField()),
                ("path", models.TextField()),
                (
                    "release",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="files",
                        to="jobserver.release",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="files",
                        to="jobserver.workspace",
                    ),
                ),
            ],
        ),
    ]
