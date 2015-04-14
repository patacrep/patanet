# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import generator.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0005_auto_20150324_2227'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='layout',
            options={'ordering': ['user_id', 'id'], 'verbose_name': 'Mise en page'},
        ),
        migrations.AlterField(
            model_name='layout',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, related_name='layouts'),
            preserve_default=True,
        ),
    ]
