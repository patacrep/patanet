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

"""Songs views"""

import os

import re

from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q
from django.conf import settings


from generator.decorators import CurrentSongbookMixin
from generator.models import Song, Artist
from generator.songs import parse_song
from generator.views.utils import LetterListView


from patanet.settings import SONGS_LIBRARY_DIR

class SongList(CurrentSongbookMixin, LetterListView):
    model = Song
    context_object_name = "song_list"
    template_name = "generator/song_list.html"
    name_field = 'title'
    queryset = Song.objects.prefetch_related('artist').order_by('slug')


class ArtistView(CurrentSongbookMixin, DetailView):
    model = Artist
    context_object_name = "artist"
    template_name = "generator/show_artist.html"


def _read_song(song):
    path = os.path.join(SONGS_LIBRARY_DIR, 'songs', song.file_path)
    return parse_song(path)


class SongView(CurrentSongbookMixin, DetailView):
    context_object_name = "song"
    model = Song
    template_name = "generator/show_song.html"

    def get_queryset(self):
        return Song.objects.filter(
                        artist__slug=self.kwargs['artist'],
                        slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(SongView, self).get_context_data(**kwargs)
        context['content'] = _read_song(context['song'])
        return context


class SongSearch(CurrentSongbookMixin, TemplateView):
    template_name = "generator/search_songs.html"

    def get_context_data(self, **kwargs):
        context = super(SongSearch, self).get_context_data(**kwargs)

        max_result = settings.MAX_SEARCH_RESULT

        query_string = self.request.GET.get('search_term', '')
        terms = _normalize_query(query_string)
        
        
        if terms:
            song_query = _get_query(terms, ['title', 'slug',])
            songs = Song.objects.filter(song_query).select_related('artist')
            context['song_list'] = songs[:max_result]
        
            artist_query = _get_query(terms, ['name', 'slug',])
            artists = Artist.objects.filter(artist_query).prefetch_related('songs')
            context['artist_list'] = artists[:max_result]
            
            context['search_terms'] = terms

        return context

def _normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def _get_query(terms, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


class ArtistList(CurrentSongbookMixin, LetterListView):
    model = Artist
    context_object_name = "artist_list"
    template_name = "generator/artist_list.html"
    name_field = 'name'
    queryset = Artist.objects.prefetch_related('songs').order_by('slug')


def random_song(request):
    song = Song.objects.order_by('?').values('slug', 'artist__slug').all()[0]
    return redirect(reverse('show_song',
                            kwargs={'artist': song['artist__slug'],
                                    'slug': song['slug']}
                            ))
