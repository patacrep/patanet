# -*- coding:utf-8 -*-
from django.contrib import admin
from generator.models import Song , Artist, Songbook, SongbooksByUser,\
    Profile
from generator.forms import SongForm

class SongAdmin(admin.ModelAdmin):
    list_display = ('title','language','artist')
    list_filter = ('artist',) 
    ordering = ('artist','title')
    
    form = SongForm
    
#     prepopulated_fields = {'slug': ('title',), }
#     #readonly_fields = ('slug',)
#     # FIXME: cas d'un slug préexistant : dans l'admin et dans la création de chant
#     fieldsets = (
#                  # Fieldset 1 : meta-info (titre, auteur...)
#                  ('Général', {
#                  'fields': ('title', 'artist','language','capo') }),
#                  # Fieldset 2 : contenu du chant
#                  ('Contenu du chant', {
#                  'fields': ('content', ) }),
#                 # Fieldset 3 : slug
#                 ('URL du chant', {
#                 'fields': ('slug', ) }),
#                  )


class ArtistAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',), }
    # FIXME: cas d'un slug préexistant


####################################################

admin.site.register(Song,SongAdmin)
admin.site.register(Artist,ArtistAdmin)
admin.site.register(Songbook)
admin.site.register(SongbooksByUser)
admin.site.register(Profile)