# Generated by Django 5.1.4 on 2025-02-12 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('buyer', 'Buyer'), ('seller', 'Seller'), ('manager', 'Manager')], default='buyer', max_length=10),
        ),
    ]
