# Generated by Django 5.1.2 on 2024-12-01 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0003_alter_preferences_goal_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
