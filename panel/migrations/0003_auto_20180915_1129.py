# Generated by Django 2.1.1 on 2018-09-15 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0002_auto_20180912_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='level',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='user',
            name='state',
            field=models.IntegerField(default=0),
        ),
    ]
