# Generated by Django 4.2.1 on 2023-05-29 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ('-id',), 'verbose_name': 'Follow', 'verbose_name_plural': 'Follows'},
        ),
    ]