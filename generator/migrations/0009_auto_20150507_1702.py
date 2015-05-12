# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import generator.models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0008_auto_20150427_2053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='papersize',
            name='bindingoffset',
            field=models.PositiveIntegerField(verbose_name='Reliure', default=0, help_text='en mm'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='papersize',
            name='bottom',
            field=models.PositiveIntegerField(verbose_name='Marge en bas', default=15, help_text='en mm'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='papersize',
            name='height',
            field=models.PositiveIntegerField(verbose_name='Hauteur', help_text='en mm'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='papersize',
            name='left',
            field=models.PositiveIntegerField(verbose_name='Marge à gauche', default=15, help_text='en mm'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='papersize',
            name='right',
            field=models.PositiveIntegerField(verbose_name='Marge à droite', default=15, help_text='en mm'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='papersize',
            name='top',
            field=models.PositiveIntegerField(verbose_name='Marge en haut', default=15, help_text='en mm'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='papersize',
            name='width',
            field=models.PositiveIntegerField(verbose_name='Largeur', help_text='en mm'),
            preserve_default=True,
        ),
    ]
