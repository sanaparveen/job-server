# Generated by Django 4.0.6 on 2022-07-25 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0028_fix_org_logos_upload_path"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="releasefile",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("deleted_at", None), ("deleted_by", None)),
                    models.Q(("deleted_at", None), ("deleted_by", None), _negated=True),
                    _connector="OR",
                ),
                name="jobserver_releasefile_deleted_fields_both_set",
            ),
        ),
    ]
