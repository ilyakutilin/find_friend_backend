# Generated by Django 5.0.2 on 2024-03-06 16:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_friendrequest_friendship_alter_user_friends_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="friendship",
            options={"verbose_name": "Друг", "verbose_name_plural": "Друзья"},
        ),
    ]