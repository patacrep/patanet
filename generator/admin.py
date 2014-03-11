# -*- coding:utf-8 -*-
from django.contrib import admin
from generator.models import Song, Artist, Songbook, \
                            ItemsInSongbook, Section


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
#admin.site.register(SongbooksByUser)
#admin.site.register(Profile)
admin.site.register(ItemsInSongbook)
admin.site.register(Section)
