# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import generator.models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='itemsinsongbook',
            unique_together=set([('item_id', 'item_type', 'songbook')]),
        ),
    ]
