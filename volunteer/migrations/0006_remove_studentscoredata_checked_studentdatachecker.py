# Generated by Django 4.2.3 on 2024-01-14 03:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("volunteer", "0005_studentscoredata_checked"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="studentscoredata",
            name="checked",
        ),
        migrations.CreateModel(
            name="StudentDataChecker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("checked", models.BooleanField(default=False, verbose_name="Checked")),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Student Information",
                    ),
                ),
            ],
        ),
    ]
