# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Artist'
        db.create_table(u'generator_artist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'generator', ['Artist'])

        # Adding model 'Song'
        db.create_table(u'generator_song', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=7, null=True)),
            ('capo', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='songs', to=orm['generator.Artist'])),
            ('file', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['generator.GitFile'], unique=True)),
        ))
        db.send_create_signal(u'generator', ['Song'])

        # Adding model 'Songbook'
        db.create_table(u'generator_songbook', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('bookoptions', self.gf('jsonfield.fields.JSONField')()),
            ('booktype', self.gf('django.db.models.fields.CharField')(default='chrd', max_length=4)),
            ('template', self.gf('django.db.models.fields.CharField')(default='patacrep.tmpl', max_length=100)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='songbooks', to=orm['generator.Profile'])),
        ))
        db.send_create_signal(u'generator', ['Songbook'])

        # Adding model 'Section'
        db.create_table(u'generator_section', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'generator', ['Section'])

        # Adding model 'ItemsInSongbook'
        db.create_table(u'generator_itemsinsongbook', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('item_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('songbook', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.Songbook'])),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'generator', ['ItemsInSongbook'])

        # Adding model 'SongInSongbook'
        db.create_table(u'generator_songinsongbook', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=7, null=True)),
            ('capo', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(related_name='song_in_songbooks', null=True, to=orm['generator.Song'])),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='songs_in_songbooks', to=orm['generator.ArtistInSongbook'])),
            ('file', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['generator.FileInSongbook'], unique=True)),
        ))
        db.send_create_signal(u'generator', ['SongInSongbook'])

        # Adding model 'ArtistInSongbook'
        db.create_table(u'generator_artistinsongbook', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='artistinsongbook_set', null=True, on_delete=models.SET_NULL, to=orm['generator.Artist'])),
        ))
        db.send_create_signal(u'generator', ['ArtistInSongbook'])

        # Adding model 'Profile'
        db.create_table(u'generator_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal(u'generator', ['Profile'])

        # Adding model 'GitFile'
        db.create_table(u'generator_gitfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file_path', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('commit_hash', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('object_hash', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'generator', ['GitFile'])

        # Adding model 'FileInSongbook'
        db.create_table(u'generator_fileinsongbook', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file_path', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('commit_hash', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('object_hash', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'generator', ['FileInSongbook'])


    def backwards(self, orm):
        # Deleting model 'Artist'
        db.delete_table(u'generator_artist')

        # Deleting model 'Song'
        db.delete_table(u'generator_song')

        # Deleting model 'Songbook'
        db.delete_table(u'generator_songbook')

        # Deleting model 'Section'
        db.delete_table(u'generator_section')

        # Deleting model 'ItemsInSongbook'
        db.delete_table(u'generator_itemsinsongbook')

        # Deleting model 'SongInSongbook'
        db.delete_table(u'generator_songinsongbook')

        # Deleting model 'ArtistInSongbook'
        db.delete_table(u'generator_artistinsongbook')

        # Deleting model 'Profile'
        db.delete_table(u'generator_profile')

        # Deleting model 'GitFile'
        db.delete_table(u'generator_gitfile')

        # Deleting model 'FileInSongbook'
        db.delete_table(u'generator_fileinsongbook')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'generator.artist': {
            'Meta': {'ordering': "['name']", 'object_name': 'Artist'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'generator.artistinsongbook': {
            'Meta': {'ordering': "['name']", 'object_name': 'ArtistInSongbook'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'artistinsongbook_set'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['generator.Artist']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'generator.fileinsongbook': {
            'Meta': {'object_name': 'FileInSongbook'},
            'commit_hash': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'file_path': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_hash': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'generator.gitfile': {
            'Meta': {'object_name': 'GitFile'},
            'commit_hash': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'file_path': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_hash': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'generator.itemsinsongbook': {
            'Meta': {'ordering': "['rank']", 'object_name': 'ItemsInSongbook'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'item_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'songbook': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['generator.Songbook']"})
        },
        u'generator.profile': {
            'Meta': {'object_name': 'Profile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'generator.section': {
            'Meta': {'object_name': 'Section'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'generator.song': {
            'Meta': {'ordering': "['title']", 'object_name': 'Song'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'songs'", 'to': u"orm['generator.Artist']"}),
            'capo': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['generator.GitFile']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'generator.songbook': {
            'Meta': {'object_name': 'Songbook'},
            'bookoptions': ('jsonfield.fields.JSONField', [], {}),
            'booktype': ('django.db.models.fields.CharField', [], {'default': "'chrd'", 'max_length': '4'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['contenttypes.ContentType']", 'symmetrical': 'False', 'through': u"orm['generator.ItemsInSongbook']", 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'template': ('django.db.models.fields.CharField', [], {'default': "'patacrep.tmpl'", 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'songbooks'", 'to': u"orm['generator.Profile']"})
        },
        u'generator.songinsongbook': {
            'Meta': {'ordering': "['title']", 'object_name': 'SongInSongbook'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'songs_in_songbooks'", 'to': u"orm['generator.ArtistInSongbook']"}),
            'capo': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['generator.FileInSongbook']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'song_in_songbooks'", 'null': 'True', 'to': u"orm['generator.Song']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['generator']