# Generated by Django 4.0.1 on 2022-01-31 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0007_rename_org_github_orgs2_to_github_orgs"),
    ]

    operations = [
        migrations.AddField(
            model_name="workspace",
            name="uses_new_release_flow",
            field=models.BooleanField(default=True),
        ),
    ]
