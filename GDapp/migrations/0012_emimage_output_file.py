# Generated by Django 3.1.4 on 2020-12-21 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GDapp', '0011_merge_20201215_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='emimage',
            name='output_file',
            field=models.FileField(null=True, upload_to='analyzed/output'),
        ),
    ]
