# Generated by Django 3.0 on 2019-12-12 08:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='offer_type_id',
        ),
    ]
