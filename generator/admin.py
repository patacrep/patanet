# -*- coding: utf-8 -*-
#    Copyright (C) 2014 The Patacrep Team
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from generator.models import Song, Artist, Songbook, Task, Layout


class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'artist')
    list_filter = ('artist',)
    ordering = ('artist', 'title')

admin.site.register(Song, SongAdmin)


class ArtistAdmin(admin.ModelAdmin):

    def song_number(self, artist):
        return artist.songs.all().count()

    song_number.short_description = _(u'nombre de chants')

    list_display = ('name', 'song_number',)
    ordering = ('name',)

admin.site.register(Artist, ArtistAdmin)


class SongbookAdmin(admin.ModelAdmin):
    def truncated_description(self, songbook):
        '''Truncate the songbook description'''
        text = songbook.description[0:80]
        if len(songbook.description) > 80:
            return text + '...'
        else:
            return text

    truncated_description.short_description = _(u'description')

    def song_number(self, songbook):
        return songbook.count_songs()

    song_number.short_description = _(u'nombre de chants')

    list_display = ('title',
                    'user',
                    'truncated_description',
                    'song_number',
                    'is_public')
    list_filter = ('user',)
    ordering = ('user', 'title')

admin.site.register(Songbook, SongbookAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('songbook', 'user', 'layout', 'last_updated', 'state')
    ordering = ('state',)

    def user(self, task):
        return task.songbook.user

admin.site.register(Task, TaskAdmin)


class LayoutAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Layout, LayoutAdmin)
