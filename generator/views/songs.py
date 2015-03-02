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


from django.views.generic import ListView, DetailView
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
import random

from generator.decorators import CurrentSongbookMixin
from generator.models import Song, Artist
from generator.name_paginator import NamePaginator
from generator.songs import parse_song


from patanet.settings import SONGS_LIBRARY_DIR

class SongList(CurrentSongbookMixin, ListView):
    model = Song
    context_object_name = "song_list"
    template_name = "generator/song_list.html"
    paginate_by = 10
    paginator_class = NamePaginator
    queryset = Song.objects.prefetch_related('artist').all().order_by('slug')


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


class ArtistList(CurrentSongbookMixin, ListView):
    model = Artist
    context_object_name = "artist_list"
    template_name = "generator/artist_list.html"
    paginate_by = 10
    paginator_class = NamePaginator
    queryset = Artist.objects.prefetch_related('songs').order_by('slug')


def random_song(request):
    count = Song.objects.all().count()
    random_index = random.randrange(0, count) # to have a number between 0 and count -1
    song = Song.objects.values('slug', 'artist__slug').all()[random_index]
    return redirect(reverse('show_song',
                            kwargs={'artist': song['artist__slug'],
                                    'slug': song['slug']}
                            ))
