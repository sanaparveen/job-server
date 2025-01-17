# Generated by Django 4.0.4 on 2022-06-08 15:42

from django.db import migrations


def copy_requested_actions_to_requested_actions2(apps, schema_editor):
    JobRequest = apps.get_model("jobserver", "JobRequest")

    for job_request in JobRequest.objects.all():
        job_request.requested_actions2 = job_request.requested_actions
        job_request.save(update_fields=["requested_actions2"])


def clear_requested_actions2(apps, schema_editor):
    JobRequest = apps.get_model("jobserver", "JobRequest")
    JobRequest.objects.update(requested_actions2=[])


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0012_add_job_request_requested_actions2"),
    ]

    operations = [
        migrations.RunPython(
            copy_requested_actions_to_requested_actions2,
            reverse_code=clear_requested_actions2,
        )
    ]
