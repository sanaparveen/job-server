# Generated by Django 3.2.5 on 2021-11-05 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0003_add_application_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="studypurposepage",
            name="is_covid_prevention",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="studypurposepage",
            name="is_covid_vaccine_effectiveness_or_safety",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="studypurposepage",
            name="is_covid_vaccine_eligibility_or_coverage",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="studypurposepage",
            name="is_other_impacts_of_covid",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="studypurposepage",
            name="is_post_covid_health_impacts",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="studypurposepage",
            name="is_risk_from_covid",
            field=models.BooleanField(default=False),
        ),
    ]