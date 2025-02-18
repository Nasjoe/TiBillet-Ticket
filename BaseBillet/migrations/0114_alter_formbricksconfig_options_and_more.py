# Generated by Django 4.2.17 on 2025-02-18 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BaseBillet', '0113_event_easy_reservation_alter_event_categorie_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='formbricksconfig',
            options={'verbose_name': 'Configuration Formbrick', 'verbose_name_plural': 'Configurations Formbrick'},
        ),
        migrations.AlterModelOptions(
            name='formbricksforms',
            options={'verbose_name': 'Formulaire', 'verbose_name_plural': 'Formulaires'},
        ),
        migrations.AlterField(
            model_name='event',
            name='easy_reservation',
            field=models.BooleanField(default=False, help_text='Mode réservation en un clic si user connecté.', verbose_name='Réservation facile'),
        ),
    ]
