# Generated by Django 3.2.8 on 2022-03-28 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_auto_20220328_2148"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bill",
            name="status",
            field=models.CharField(default="PENDING", max_length=16),
        ),
    ]
