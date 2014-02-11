# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FileInSongbook'
        db.create_table(u'generator_fileinsongbook', (
            (u'gitfile_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['generator.GitFile'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'generator', ['FileInSongbook'])

        # Adding model 'ArtistInSongbook'
        db.create_table(u'generator_artistinsongbook', (
            (u'artist_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['generator.Artist'], unique=True, primary_key=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='songbooks', null=True, to=orm['generator.Artist'])),
        ))
        db.send_create_signal(u'generator', ['ArtistInSongbook'])

        # Adding model 'SongInSongbook'
        db.create_table(u'generator_songinsongbook', (
            (u'song_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['generator.Song'], unique=True, primary_key=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(related_name='songbooks', null=True, to=orm['generator.Song'])),
        ))
        db.send_create_signal(u'generator', ['SongInSongbook'])


    def backwards(self, orm):
        # Deleting model 'FileInSongbook'
        db.delete_table(u'generator_fileinsongbook')

        # Deleting model 'ArtistInSongbook'
        db.delete_table(u'generator_artistinsongbook')

        # Deleting model 'SongInSongbook'
        db.delete_table(u'generator_songinsongbook')


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
            'Meta': {'ordering': "['name']", 'object_name': 'ArtistInSongbook', '_ormbases': [u'generator.Artist']},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'songbooks'", 'null': 'True', 'to': u"orm['generator.Artist']"}),
            u'artist_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['generator.Artist']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'generator.fileinsongbook': {
            'Meta': {'object_name': 'FileInSongbook', '_ormbases': [u'generator.GitFile']},
            u'gitfile_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['generator.GitFile']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'generator.gitfile': {
            'Meta': {'object_name': 'GitFile'},
            'commit_hash': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'file_path': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_hash': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'generator.itemsinsongbook': {
            'Meta': {'object_name': 'ItemsInSongbook'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'item_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'songbook': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['generator.Songbook']"})
        },
        u'generator.profile': {
            'Meta': {'object_name': 'Profile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'songbooks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'songbooks'", 'blank': 'True', 'through': u"orm['generator.SongbooksByUser']", 'to': u"orm['generator.Songbook']"}),
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
            'file': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['generator.GitFile']", 'unique': 'True', 'null': 'True'}),
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
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'items'", 'blank': 'True', 'through': u"orm['generator.ItemsInSongbook']", 'to': u"orm['contenttypes.ContentType']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'template': ('django.db.models.fields.CharField', [], {'default': "'patacrep.tmpl'", 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'users'", 'blank': 'True', 'through': u"orm['generator.SongbooksByUser']", 'to': u"orm['generator.Profile']"})
        },
        u'generator.songbooksbyuser': {
            'Meta': {'object_name': 'SongbooksByUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_owner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'songbook': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['generator.Songbook']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['generator.Profile']"})
        },
        u'generator.songinsongbook': {
            'Meta': {'ordering': "['title']", 'object_name': 'SongInSongbook', '_ormbases': [u'generator.Song']},
            'song': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'songbooks'", 'null': 'True', 'to': u"orm['generator.Song']"}),
            u'song_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['generator.Song']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['generator']