# Generated by Django 4.2.3 on 2023-07-25 16:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='user',
            new_name='first_name',
        ),
    ]
