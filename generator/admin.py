# -*- coding:utf-8 -*-
# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt


from django.contrib import admin
from generator.models import Song, Artist, Songbook


class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'artist')
    list_filter = ('artist',)
    ordering = ('artist', 'title')


class ArtistAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',), }
    # FIXME: cas d'un slug préexistant

####################################################

admin.site.register(Song, SongAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Songbook)
