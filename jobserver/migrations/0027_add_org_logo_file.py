# Generated by Django 4.0.6 on 2022-07-14 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0026_convert_user_username_to_text_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="org",
            name="logo_file",
            field=models.FileField(null=True, upload_to="uploads/orgs/"),
        ),
    ]
