# Generated by Django 2.2.20 on 2021-08-12 19:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forex', '0006_auto_20210812_2113'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='date',
            field=models.DateField(default=datetime.datetime(2021, 8, 12, 21, 46, 56, 720542), help_text='Transaction Date', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount_EGP',
            field=models.FloatField(blank=True, help_text='EGP', null=True, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount_USD',
            field=models.FloatField(blank=True, help_text='USD', null=True, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='deliverd_rate',
            field=models.FloatField(help_text='Delivered', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='paid',
            field=models.BooleanField(default=False, help_text='Paid', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='real_rate',
            field=models.FloatField(help_text='Real', verbose_name=''),
        ),
    ]