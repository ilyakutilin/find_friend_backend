# Generated by Django 5.0.2 on 2024-02-19 11:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_add_interests"),
    ]

    operations = [
        migrations.CreateModel(
            name="City",
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
                        max_length=150,
                        unique=True,
                        verbose_name="Название города",
                    ),
                ),
            ],
            options={
                "verbose_name": "Город",
                "verbose_name_plural": "Города",
                "ordering": ["name"],
            },
        ),
        migrations.AlterField(
            model_name="user",
            name="city",
            field=models.ForeignKey(
                blank=True,
                help_text="Город проживания",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="users.city",
                verbose_name="Город",
            ),
        ),
    ]