# Generated by Django 5.0.2 on 2024-02-19 12:44

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="event_price",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=10,
                verbose_name="Стоимость мероприятия",
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="event_type",
            field=models.CharField(
                max_length=50, verbose_name="Тип мероприятия"
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="name",
            field=models.CharField(
                max_length=50, verbose_name="Название мероприятия"
            ),
        ),
    ]