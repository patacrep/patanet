# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Nom')),
                ('slug', models.SlugField(unique=True, max_length=100)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Artist',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemsInSongbook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item_id', models.PositiveIntegerField()),
                ('rank', models.IntegerField(verbose_name='position')),
                ('item_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['rank'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Layout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='nom de la mise en page')),
                ('booktype', models.CharField(default=b'chorded', max_length=10, verbose_name='songbook type', choices=[(b'chorded', 'With chords'), (b'lyric', 'No Chords')])),
                ('bookoptions', jsonfield.fields.JSONField()),
                ('other_options', jsonfield.fields.JSONField()),
                ('template', models.CharField(default=b'data.tex', max_length=100, verbose_name='template')),
            ],
            options={
                'verbose_name': 'Mise en page',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='section name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('slug', models.SlugField(unique=True, max_length=100)),
                ('language', models.CharField(max_length=7, null=True, choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('capo', models.IntegerField(null=True, blank=True)),
                ('file_path', models.CharField(max_length=500)),
                ('object_hash', models.CharField(max_length=50)),
                ('artist', models.ForeignKey(related_name=b'songs', verbose_name='Artist', to='generator.Artist')),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'song',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Songbook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('slug', models.SlugField(max_length=100)),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('is_public', models.BooleanField(default=False, verbose_name='Public songbook')),
                ('author', models.CharField(default=b'', max_length=255, verbose_name='auteur')),
                ('items', models.ManyToManyField(to='contenttypes.ContentType', through='generator.ItemsInSongbook', blank=True)),
                ('user', models.ForeignKey(related_name=b'songbooks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'songbook',
                'verbose_name_plural': 'songbooks',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hash', models.CharField(max_length=40, verbose_name='contents')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='derni\xe8re mise \xe0 jour')),
                ('state', models.CharField(max_length=20, verbose_name='state', choices=[(b'QUEUED', b'Queued'), (b'IN_PROCESS', b'In process'), (b'FINISHED', b'Finished'), (b'ERROR', b'Error')])),
                ('result', jsonfield.fields.JSONField(verbose_name='result')),
                ('layout', models.ForeignKey(verbose_name='Mise en page', to='generator.Layout')),
                ('songbook', models.ForeignKey(related_name=b'tasks', verbose_name='carnet', to='generator.Songbook')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='itemsinsongbook',
            name='songbook',
            field=models.ForeignKey(to='generator.Songbook'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='itemsinsongbook',
            unique_together=set([('item_id', 'songbook')]),
        ),
    ]
