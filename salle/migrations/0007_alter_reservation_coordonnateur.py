# Generated by Django 5.2.1 on 2025-05-19 03:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salle', '0006_alter_reservation_coordonnateur'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='coordonnateur',
            field=models.ForeignKey(default='3', on_delete=django.db.models.deletion.PROTECT, to='salle.coordonateur'),
            preserve_default=False,
        ),
    ]
