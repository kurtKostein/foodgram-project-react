# Generated by Django 3.2.5 on 2021-07-25 14:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_managers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='login',
            new_name='username',
        ),
    ]