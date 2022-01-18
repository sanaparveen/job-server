# Generated by Django 3.2.10 on 2021-12-22 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "jobserver",
            "0002_mark_backend_parent_directory_and_level_4_url_as_not_required",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="backend",
            name="is_active",
            field=models.BooleanField(
                default=False,
                help_text="Is this backend currently active on the platform?  Connectivity warnings are only shown for active backends.",
            ),
        ),
    ]