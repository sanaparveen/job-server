# Generated by Django 4.1 on 2022-09-26 10:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0050_add_workspace_signed_off_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="repo",
            name="researcher_signed_off_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="repo",
            name="researcher_signed_off_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="repos_signed_off_by_researcher",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
