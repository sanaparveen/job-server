# Generated by Django 4.0.4 on 2022-06-08 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0014_remove_job_request_requested_actions"),
    ]

    operations = [
        migrations.RenameField(
            model_name="jobrequest",
            old_name="requested_actions2",
            new_name="requested_actions",
        ),
    ]