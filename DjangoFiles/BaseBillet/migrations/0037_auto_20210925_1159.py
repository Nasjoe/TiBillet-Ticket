# Generated by Django 2.2 on 2021-09-25 07:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BaseBillet', '0036_auto_20210925_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lignearticle',
            name='reservation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseBillet.Reservation'),
        ),
    ]
