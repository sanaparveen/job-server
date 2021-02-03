# Generated by Django 3.1.2 on 2020-12-07 11:51

from django.db import migrations


def link_to_backends(apps, schema_editor):
    Backend = apps.get_model("jobserver", "Backend")
    JobRequest = apps.get_model("jobserver", "JobRequest")

    for backend in Backend.objects.all():
        JobRequest.objects.filter(backend_old=backend.name.lower()).update(
            backend=backend
        )


def unlink_to_backends(apps, schema_editor):
    JobRequest = apps.get_model("jobserver", "JobRequest")

    JobRequest.objects.exclude(backend=None).update(backend=None)


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0050_add_jobrequest_backend_fk_to_backend"),
    ]

    operations = [
        migrations.RunPython(link_to_backends, reverse_code=unlink_to_backends)
    ]