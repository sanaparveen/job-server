# Generated by Django 4.0.1 on 2022-01-28 09:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0006_remove_org_github_orgs"),
    ]

    operations = [
        migrations.RenameField(
            model_name="org",
            old_name="github_orgs2",
            new_name="github_orgs",
        ),
    ]