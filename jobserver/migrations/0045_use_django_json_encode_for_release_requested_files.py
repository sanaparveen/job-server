# Generated by Django 4.0.7 on 2022-08-23 15:49

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0044_add_review_fields_to_release_and_releasefile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="release",
            name="requested_files",
            field=models.JSONField(
                encoder=django.core.serializers.json.DjangoJSONEncoder
            ),
        ),
    ]
