# Generated by Django 3.0.7 on 2020-10-08 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0005_remove_job_backend"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="job",
            name="callback_url",
        ),
        migrations.RemoveField(
            model_name="job",
            name="force_run_dependencies",
        ),
        migrations.AddField(
            model_name="jobrequest",
            name="callback_url",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="jobrequest",
            name="force_run",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="jobrequest",
            name="force_run_dependencies",
            field=models.BooleanField(default=False),
        ),
    ]