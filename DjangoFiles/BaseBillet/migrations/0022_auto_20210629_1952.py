# Generated by Django 2.2 on 2021-06-29 15:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BaseBillet', '0021_auto_20210629_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lignearticle',
            name='reservation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BaseBillet.Reservation', verbose_name='lignes_article'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservation', to='BaseBillet.Event'),
        ),
    ]
