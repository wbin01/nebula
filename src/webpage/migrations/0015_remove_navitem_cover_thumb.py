# Generated by Django 5.1.2 on 2024-10-18 04:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webpage', '0014_alter_navitem_cover_thumb'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='navitem',
            name='cover_thumb',
        ),
    ]
