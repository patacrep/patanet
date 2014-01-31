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
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.Artist'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=7, null=True)),
            ('capo', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['generator.GitFile'], unique=True, null=True)),
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
        ))
        db.send_create_signal(u'generator', ['Songbook'])

        # Adding model 'SectionInSongbooks'
        db.create_table(u'generator_sectioninsongbooks', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='main section', max_length=200)),
        ))
        db.send_create_signal(u'generator', ['SectionInSongbooks'])

        # Adding model 'SongsInSongbooks'
        db.create_table(u'generator_songsinsongbooks', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.Song'])),
            ('songbook', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.Songbook'])),
            ('rank_in_section', self.gf('django.db.models.fields.IntegerField')()),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.SectionInSongbooks'])),
        ))
        db.send_create_signal(u'generator', ['SongsInSongbooks'])

        # Adding model 'Profile'
        db.create_table(u'generator_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal(u'generator', ['Profile'])

        # Adding model 'SongbooksByUser'
        db.create_table(u'generator_songbooksbyuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_owner', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.Profile'])),
            ('songbook', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.Songbook'])),
        ))
        db.send_create_signal(u'generator', ['SongbooksByUser'])

        # Adding model 'GitFile'
        db.create_table(u'generator_gitfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file_path', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('file_version', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'generator', ['GitFile'])


    def backwards(self, orm):
        # Deleting model 'Artist'
        db.delete_table(u'generator_artist')

        # Deleting model 'Song'
        db.delete_table(u'generator_song')

        # Deleting model 'Songbook'
        db.delete_table(u'generator_songbook')

        # Deleting model 'SectionInSongbooks'
        db.delete_table(u'generator_sectioninsongbooks')

        # Deleting model 'SongsInSongbooks'
        db.delete_table(u'generator_songsinsongbooks')

        # Deleting model 'Profile'
        db.delete_table(u'generator_profile')

        # Deleting model 'SongbooksByUser'
        db.delete_table(u'generator_songbooksbyuser')

        # Deleting model 'GitFile'
        db.delete_table(u'generator_gitfile')


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
            'Meta': {'object_name': 'Artist'},
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
        u'generator.profile': {
            'Meta': {'object_name': 'Profile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'songbooks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'songbooks'", 'blank': 'True', 'through': u"orm['generator.SongbooksByUser']", 'to': u"orm['generator.Songbook']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'generator.sectioninsongbooks': {
            'Meta': {'object_name': 'SectionInSongbooks'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'main section'", 'max_length': '200'})
        },
        u'generator.song': {
            'Meta': {'object_name': 'Song'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['generator.Artist']"}),
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'songs': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'songs'", 'blank': 'True', 'through': u"orm['generator.SongsInSongbooks']", 'to': u"orm['generator.Song']"}),
            'template': ('django.db.models.fields.CharField', [], {'default': "'patacrep.tmpl'", 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'generator.songbooksbyuser': {
            'Meta': {'object_name': 'SongbooksByUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_owner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'songbook': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['generator.Songbook']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['generator.Profile']"})
        },
        u'generator.songsinsongbooks': {
            'Meta': {'object_name': 'SongsInSongbooks'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rank_in_section': ('django.db.models.fields.IntegerField', [], {}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['generator.SectionInSongbooks']"}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['generator.Song']"}),
            'songbook': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['generator.Songbook']"})
        }
    }

    complete_apps = ['generator']