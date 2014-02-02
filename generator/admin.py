# -*- coding:utf-8 -*-
from django.contrib import admin
from generator.models import Song , Artist, Songbook, SongbooksByUser, \
                            Profile, SongsInSongbooks
from generator.forms import SongForm

class SongAdmin(admin.ModelAdmin):
    list_display = ('title','language','artist')
    list_filter = ('artist',) 
    ordering = ('artist','title')
    form = SongForm


class ArtistAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',), }
    # FIXME: cas d'un slug préexistant

class SgInSbAdmin(admin.ModelAdmin):
    list_display = ('rank_in_section','section','__unicode__')
    ordering = ('section','rank_in_section')

####################################################

admin.site.register(Song,SongAdmin)
admin.site.register(Artist,ArtistAdmin)
admin.site.register(Songbook)
#admin.site.register(SongbooksByUser)
#admin.site.register(Profile)
admin.site.register(SongsInSongbooks,SgInSbAdmin)