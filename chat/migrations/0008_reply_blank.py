# Generated by Django 3.0.2 on 2020-02-14 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0007_statement_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statement',
            name='reply',
            field=models.TextField(blank=True, default=''),
        ),
    ]
