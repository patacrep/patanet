# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import generator.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('generator', '0002_auto_20150315_2304'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='layout',
            options={'verbose_name': 'Mise en page', 'ordering': ['user_id']},
        ),
        migrations.AddField(
            model_name='layout',
            name='user',
            field=models.ForeignKey(related_name='layouts', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
    ]
