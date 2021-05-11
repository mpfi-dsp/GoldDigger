# Generated by Django 3.1.4 on 2021-04-16 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GDapp', '0029_auto_20210415_1330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emimage',
            name='thresh_sens',
            field=models.FloatField(default=4.0, help_text='Use arrows or type in decimal values if desired.'),
        ),
    ]