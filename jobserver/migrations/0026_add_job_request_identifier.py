# Generated by Django 3.1.2 on 2020-11-11 16:16

from django.db import migrations, models

import jobserver.models


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0025_remove_user_selected_workspace"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobrequest",
            name="identifier",
            field=models.TextField(default=jobserver.models.new_id),
        ),
    ]