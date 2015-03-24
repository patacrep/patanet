# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import generator.models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0003_auto_20150324_2221'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='task',
            unique_together=set([('songbook', 'layout')]),
        ),
    ]
