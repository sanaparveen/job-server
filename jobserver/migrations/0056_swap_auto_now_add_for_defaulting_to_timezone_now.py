# Generated by Django 3.1.2 on 2020-12-22 14:45

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0055_add_workspace_is_archived"),
    ]

    operations = [
        migrations.AlterField(
            model_name="backend",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="job",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="jobrequest",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="workspace",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]