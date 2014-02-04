# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'SongsInSongbooks', fields ['section', 'rank_in_section']
        db.delete_unique(u'generator_songsinsongbooks', ['section_id', 'rank_in_section'])

        # Deleting model 'SectionInSongbooks'
        db.delete_table(u'generator_sectioninsongbooks')

        # Deleting model 'SongsInSongbooks'
        db.delete_table(u'generator_songsinsongbooks')

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


    def backwards(self, orm):
        # Adding model 'SectionInSongbooks'
        db.create_table(u'generator_sectioninsongbooks', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='main section', max_length=200)),
        ))
        db.send_create_signal(u'generator', ['SectionInSongbooks'])

        # Adding model 'SongsInSongbooks'
        db.create_table(u'generator_songsinsongbooks', (
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(related_name='section', to=orm['generator.SectionInSongbooks'])),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.Song'])),
            ('songbook', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.Songbook'])),
            ('rank_in_section', self.gf('django.db.models.fields.IntegerField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'generator', ['SongsInSongbooks'])

        # Adding unique constraint on 'SongsInSongbooks', fields ['section', 'rank_in_section']
        db.create_unique(u'generator_songsinsongbooks', ['section_id', 'rank_in_section'])

        # Deleting model 'Section'
        db.delete_table(u'generator_section')

        # Deleting model 'ItemsInSongbook'
        db.delete_table(u'generator_itemsinsongbook')


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
        u'generator.gitfile': {
            'Meta': {'object_name': 'GitFile'},
            'file_path': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'file_version': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
        }
    }

    complete_apps = ['generator']