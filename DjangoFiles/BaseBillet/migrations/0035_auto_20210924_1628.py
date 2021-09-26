# Generated by Django 2.2 on 2021-09-24 12:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BaseBillet', '0034_auto_20210924_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='stripe_mode_test',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='lignearticle',
            name='reservation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseBillet.Reservation'),
        ),
    ]
