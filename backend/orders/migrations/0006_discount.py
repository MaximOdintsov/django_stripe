# Generated by Django 4.1.7 on 2023-02-20 19:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_alter_tax_options_order_tax_alter_tax_inclusive'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=3, verbose_name='Currency')),
                ('percent_off', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Discount percentage')),
                ('max_redemptions', models.IntegerField(default=100, verbose_name='Max redemptions')),
            ],
        ),
    ]
