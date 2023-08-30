# Generated by Django 4.2.4 on 2023-08-29 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('convert', '0012_remove_exchangerates_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencyconvert',
            name='input_currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='input_rate', to='convert.exchangerates'),
        ),
        migrations.AlterField(
            model_name='currencyconvert',
            name='output_currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='output_rate', to='convert.exchangerates'),
        ),
    ]