# Generated by Django 5.0.2 on 2024-02-12 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gui', '0010_dogadoptionpost_size_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='registration_code',
            field=models.CharField(max_length=100),
        ),
    ]
