# Generated by Django 5.0.2 on 2024-02-11 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gui', '0008_alter_shelter_working_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='shelter',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
