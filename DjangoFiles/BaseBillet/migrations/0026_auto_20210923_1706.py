# Generated by Django 2.2 on 2021-09-23 13:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BaseBillet', '0025_auto_20210923_1403'),
    ]

    operations = [
        migrations.CreateModel(
            name='VAT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent', models.FloatField(verbose_name='Taux de TVA (%)')),
            ],
            options={
                'verbose_name': 'TVA',
                'verbose_name_plural': 'TVA',
            },
        ),
        migrations.AlterField(
            model_name='lignearticle',
            name='reservation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseBillet.Reservation'),
        ),
        migrations.AddField(
            model_name='article',
            name='vat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='BaseBillet.VAT', verbose_name='TVA'),
        ),
    ]
