# Generated by Django 4.2.17 on 2024-12-13 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BaseBillet', '0102_configuration_federated_with'),
    ]

    operations = [
        migrations.AlterField(
            model_name='optiongenerale',
            name='poids',
            field=models.PositiveIntegerField(db_index=True, default=0, verbose_name='Poids'),
        ),
    ]
