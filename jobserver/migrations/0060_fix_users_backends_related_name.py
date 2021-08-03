# Generated by Django 3.2.5 on 2021-07-27 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0059_add_backend_level_4_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="backends",
            field=models.ManyToManyField(
                related_name="members",
                through="jobserver.BackendMembership",
                to="jobserver.Backend",
            ),
        ),
    ]
