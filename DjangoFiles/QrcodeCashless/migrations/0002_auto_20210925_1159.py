# Generated by Django 2.2 on 2021-09-25 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QrcodeCashless', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartecashless',
            old_name='uuid_qrcode',
            new_name='uuid',
        ),
        migrations.AlterField(
            model_name='cartecashless',
            name='number',
            field=models.CharField(db_index=True, default=0, max_length=8, unique=True),
            preserve_default=False,
        ),
    ]
