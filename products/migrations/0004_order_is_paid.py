# Generated by Django 5.1 on 2024-08-21 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_order_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
    ]
