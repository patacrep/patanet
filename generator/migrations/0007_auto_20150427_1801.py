# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import generator.models

# Adapted from https://docs.djangoproject.com/en/1.8/topics/migrations/#data-migrations
def insert_initial(apps, schema_editor):
    Papersize = apps.get_model("generator", "Papersize")
    Papersize.objects.bulk_create([
        Papersize(id=1, name="A4", width=210, height=297, top=20, right=20, bottom=20, left=20, bindingoffset=0),
    ])



class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0006_auto_20150414_2001'),
    ]

    operations = [
        migrations.CreateModel(
            name='Papersize',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(verbose_name='nom du format', max_length=200)),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('left', models.IntegerField()),
                ('right', models.IntegerField()),
                ('top', models.IntegerField()),
                ('bottom', models.IntegerField()),
                ('bindingoffset', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Papier',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='layout',
            name='papersize',
            field=models.ForeignKey(to='generator.Papersize', related_name='layouts', default=1),
            preserve_default=True,
        ),
        migrations.RunPython(insert_initial),
    ]
