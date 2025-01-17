# Generated by Django 4.0.4 on 2022-07-01 13:05

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import redirects.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("jobserver", "0019_add_backend_alert_timeout"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Redirect",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "old_url",
                    models.TextField(
                        db_index=True,
                        validators=[redirects.models.validate_not_empty],
                    ),
                ),
                (
                    "expires_at",
                    models.DateTimeField(default=redirects.models.default_expires_at),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="redirects_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "deleted_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="redirect_deleted",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="redirects",
                        to="jobserver.project",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="redirects",
                        to="jobserver.workspace",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="redirect",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("deleted_at", None), ("deleted_by", None)),
                    models.Q(
                        models.Q(("deleted_at", None), _negated=True),
                        models.Q(("deleted_by", None), _negated=True),
                    ),
                    _connector="OR",
                ),
                name="redirects_redirect_both_deleted_at_and_deleted_by_set",
            ),
        ),
        migrations.AddConstraint(
            model_name="redirect",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("project__isnull", True), ("workspace__isnull", False)),
                    models.Q(("project__isnull", False), ("workspace__isnull", True)),
                    _connector="OR",
                ),
                name="redirects_redirect_only_one_target_model_set",
            ),
        ),
    ]
