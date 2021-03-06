# Generated by Django 3.2.8 on 2022-03-28 14:48

from django.db import migrations, models
import paytungan.app.base.constants


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_auto_20220325_2308"),
    ]

    operations = [
        migrations.AddField(
            model_name="bill",
            name="status",
            field=models.CharField(
                default="PENDING",
                max_length=16,
            ),
        ),
        migrations.AddConstraint(
            model_name="bill",
            constraint=models.UniqueConstraint(
                condition=models.Q(("deleted__isnull", True)),
                fields=("user_id", "split_bill_id"),
                name="unique_user_id_and_split_bill_id_if_not_deleted",
            ),
        ),
    ]
