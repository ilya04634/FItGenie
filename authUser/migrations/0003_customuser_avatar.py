# Generated by Django 5.1.2 on 2024-12-12 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authUser', '0002_remove_customuser_email_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
    ]