# Generated by Django 2.2 on 2021-09-23 09:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Customers', '0003_auto_20210623_1351'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarteCashless',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_id', models.CharField(db_index=True, max_length=8, unique=True)),
                ('uuid_qrcode', models.UUIDField(blank=True, null=True, verbose_name='Uuid')),
                ('number', models.CharField(blank=True, db_index=True, max_length=8, null=True, unique=True)),
                ('origine', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Customers.Client')),
            ],
        ),
    ]
