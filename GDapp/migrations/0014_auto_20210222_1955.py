# Generated by Django 3.1.4 on 2021-02-22 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GDapp', '0013_auto_20201221_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emimage',
            name='trained_model',
            field=models.CharField(choices=[('43kGoldDigger', 'GoldDigger for small particles in 43k images'), ('87kGoldDigger', 'General GoldDigger')], default='87kGoldDigger', max_length=100),
        ),
    ]
