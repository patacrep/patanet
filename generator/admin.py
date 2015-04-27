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
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from generator.models import Song, Artist, Songbook, Task, Layout, ItemsInSongbook, Papersize

import re
from django.conf import settings

def id_attr(instance):
    return "n° " + str(instance.id)

# Add a link to a related object AdminView (via ForeignKey)
# String target_model: name of model to link to
# String field:        field name in the current `instance`, so instance.field = TargetModel() 
#                      (usually the same as target_mode)
# String field_name: name of this field in the ModelAdmin class
# adapted from http://stackoverflow.com/a/13287201/3207406
def add_link_field(target_model = None, field = '', app='generator', field_name='link',
                   link_text=id_attr):
    def add_link(cls):
        reverse_name = target_model or cls.model.__name__.lower()
        def link(self, instance):
            app_name = app or instance._meta.app_label
            reverse_path = "admin:%s_%s_change" % (app_name, reverse_name)
            link_obj = getattr(instance, field, None) or instance
            if hasattr(link_obj, 'get'):
                link_obj = link_obj.get()
            url = reverse(reverse_path, args = (link_obj.id,))
            return mark_safe("<a href='%s'>%s</a>" % (url, link_text(link_obj)))
        link.allow_tags = True
        link.short_description = reverse_name + ' link'
        setattr(cls, field_name, link)
        cls.readonly_fields = list(getattr(cls, 'readonly_fields', [])) + \
            [field_name]
        return cls
    return add_link

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


@add_link_field('songbook', 'songbook', field_name="songbook_link")
@add_link_field('layout', 'layout')
class TaskAdmin(admin.ModelAdmin):
    list_display = ('songbook', 'user', 'last_updated', 'state', 'log_link', 'link', 'songbook_link', )
    readonly_fields = ('log_link',)
    ordering = ('state',)

    def user(self, task):
        return task.songbook.user


    def log_link(self, obj):
        msg = obj.result.get('error_msg', '')
        match = re.search('([^" \']+\.log)', msg)
        if(match):
            url = settings.MEDIA_URL +'PDF/' + match.group(0)
            return mark_safe("<a href='%s'>Voir les logs</a>" % url)
        return None

    log_link.allow_tags = True

admin.site.register(Task, TaskAdmin)


def make_layout_public(modeladmin, request, queryset):
    queryset.update(user_id=0)
make_layout_public.short_description = _(u'Rendre les mise en page utilisables par tous')


class LayoutAdmin(admin.ModelAdmin):
    list_display = ('name', )
    actions = [make_layout_public]

admin.site.register(Layout, LayoutAdmin)


class PapersizeAdmin(admin.ModelAdmin):
    list_display = ('name', )

admin.site.register(Papersize, PapersizeAdmin)

class ItemsInSongbookAdmin(admin.ModelAdmin):
    list_display = ('songbook_title','item','rank',)
    list_filter = ('songbook__title',)
    ordering = ('songbook','rank',)


    def songbook_title(self, obj):
        return obj.songbook.title
    songbook_title.short_description = 'Songbook'
    songbook_title.admin_order_field = 'songbook__title'

    def item(self, obj):
        try:
            title = '[Song] ' + obj.item.title + ' - ' + obj.item.artist.name
        except AttributeError:
            title = '[Section] ' + obj.item.name
        
        return title

admin.site.register(ItemsInSongbook, ItemsInSongbookAdmin)
