# Generated by Django 4.1 on 2022-10-11 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0053_add_repo_internal_signed_off_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="trace_context",
            field=models.JSONField(null=True),
        ),
    ]
