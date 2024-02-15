# Generated by Django 5.0.2 on 2024-02-15 11:19

from django.db import migrations
from pathlib import Path
from config.settings import BASE_DIR

INTERESTS_FILE = Path(BASE_DIR / "data" / "interests.txt")


def add_interests(apps, schema_editor):
    Interest = apps.get_model("users", "Interest")
    with open(INTERESTS_FILE) as f:
        interests = []
        for line in f:
            interest_name = line.strip()
            new_interest_obj = Interest(name=interest_name)
            interests.append(new_interest_obj)
        Interest.objects.bulk_create(interests)


def remove_interests(apps, schema_editor):
    Interest = apps.get_model("users", "Interest")
    with open(INTERESTS_FILE) as f:
        for line in f:
            interest_name = line.strip()
            Interest.objects.filter(name=interest_name).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [migrations.RunPython(add_interests, remove_interests)]
