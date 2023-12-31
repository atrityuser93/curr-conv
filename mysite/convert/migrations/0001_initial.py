# Generated by Django 4.2.4 on 2023-08-12 09:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currencies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=25)),
                ('code', models.CharField(default='XXX', max_length=3)),
                ('Currency', models.FloatField()),
                ('USD', models.FloatField()),
                ('fetched_on', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
