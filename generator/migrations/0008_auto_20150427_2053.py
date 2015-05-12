# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import generator.models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0007_auto_20150427_1801'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='layout',
            name='name',
        ),
    ]
