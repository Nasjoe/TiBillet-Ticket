# Generated by Django 4.2 on 2024-08-13 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BaseBillet', '0092_alter_membership_unique_together_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='asset_fedow',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
