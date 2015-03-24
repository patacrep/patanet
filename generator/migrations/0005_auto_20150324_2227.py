# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import generator.models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0004_auto_20150324_2223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='layout',
            name='bookoptions',
            field=jsonfield.fields.JSONField(default={}, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='layout',
            name='other_options',
            field=jsonfield.fields.JSONField(default={}, blank=True),
            preserve_default=True,
        ),
    ]
