# Generated by Django 3.1.4 on 2021-01-21 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GDapp', '0014_auto_20210121_1652'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocalFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('doc_file', models.FilePathField(path='/usr/src/local-images')),
            ],
        ),
    ]