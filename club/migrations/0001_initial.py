# Generated by Django 4.2.3 on 2023-07-31 06:00

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentClubData",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=30,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="student_email",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        max_length=30,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="student_email_name",
                    ),
                ),
                (
                    "student_id",
                    models.CharField(
                        max_length=20,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="student_id",
                    ),
                ),
                (
                    "student_real_name",
                    models.CharField(
                        max_length=10,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="student_real_name",
                    ),
                ),
                (
                    "is_created",
                    models.BooleanField(verbose_name="Is This Account Created"),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="EventClassInformation",
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
                (
                    "name",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="Class Name"
                    ),
                ),
                (
                    "desc",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="Class Description"
                    ),
                ),
                (
                    "max_num",
                    models.IntegerField(
                        verbose_name="Max Number of Students of the Class"
                    ),
                ),
                ("full_desc", models.TextField(verbose_name="Class Full Description")),
                (
                    "hf_desc",
                    models.BooleanField(
                        verbose_name="Whether Class Has Full Description"
                    ),
                ),
                ("forbid_chs", models.BooleanField(verbose_name="Forbidden Status")),
            ],
        ),
        migrations.CreateModel(
            name="EventClassType",
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
                (
                    "type_name",
                    models.CharField(max_length=30, verbose_name="Class Type Name"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Notice",
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
                ("title", models.CharField(max_length=50, verbose_name="Notice Title")),
                ("release_date", models.DateField(verbose_name="Notice Release Data")),
                ("content", models.TextField(verbose_name="Notice Content")),
                ("active", models.BooleanField(verbose_name="Notice Status")),
            ],
        ),
        migrations.CreateModel(
            name="StudentSelectionInformation",
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
                ("locked", models.BooleanField(verbose_name="Selection Locked Status")),
                (
                    "info_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="club.eventclassinformation",
                        verbose_name="Class Information",
                    ),
                ),
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
        migrations.CreateModel(
            name="SelectionEvent",
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
                ("start_time", models.DateTimeField(verbose_name="start time")),
                ("end_time", models.DateTimeField(verbose_name="end time")),
                (
                    "title",
                    models.CharField(max_length=100, verbose_name="selection_title"),
                ),
                (
                    "student_group",
                    models.ManyToManyField(
                        blank=True,
                        related_name="SelectionEvent_student_group",
                        to="auth.group",
                        verbose_name="Student Group Information",
                    ),
                ),
                (
                    "teachers_group",
                    models.ManyToManyField(
                        blank=True,
                        related_name="SelectionEvent_teachers_group",
                        to="auth.group",
                        verbose_name="Teachers Group Information",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EventClassTypeConstraints",
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
                ("coef_1", models.IntegerField(verbose_name="Coefficient for type 1")),
                ("coef_2", models.IntegerField(verbose_name="Coefficient for type 2")),
                ("C", models.IntegerField(verbose_name="Constant of the constraint")),
                (
                    "event_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="club.selectionevent",
                        verbose_name="Event Information",
                    ),
                ),
                (
                    "type_id1",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="EventClassTypeConstraints_type_id1",
                        to="club.eventclasstype",
                        verbose_name="Type 1",
                    ),
                ),
                (
                    "type_id2",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="EventClassTypeConstraints_type_id2",
                        to="club.eventclasstype",
                        verbose_name="Type 2",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="eventclasstype",
            name="event_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="club.selectionevent",
                verbose_name="Event Information",
            ),
        ),
        migrations.AddField(
            model_name="eventclassinformation",
            name="class_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="club.eventclasstype",
                verbose_name="Class Type Information",
            ),
        ),
        migrations.AddField(
            model_name="eventclassinformation",
            name="event_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="club.selectionevent",
                verbose_name="Event Information",
            ),
        ),
        migrations.AddField(
            model_name="eventclassinformation",
            name="user_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Teacher Information",
            ),
        ),
    ]
