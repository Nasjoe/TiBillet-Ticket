# Generated by Django 2.2 on 2021-09-24 12:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BaseBillet', '0032_auto_20210924_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='stripe_api_key',
            field=models.CharField(blank=True, max_length=110, null=True),
        ),
        migrations.AddField(
            model_name='configuration',
            name='stripe_test_api_key',
            field=models.CharField(blank=True, max_length=110, null=True),
        ),
        migrations.AlterField(
            model_name='lignearticle',
            name='reservation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseBillet.Reservation'),
        ),
    ]
