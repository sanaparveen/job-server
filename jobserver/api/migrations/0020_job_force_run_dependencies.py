# Generated by Django 3.0.7 on 2020-08-31 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_job_force_run'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='force_run_dependencies',
            field=models.BooleanField(default=False),
        ),
    ]