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

"""
Functions for song file (.sg) management.
"""
from django.utils.text import slugify
from django.utils.encoding import smart_text
from django.conf.global_settings import LANGUAGES

from patacrep.plastex import parsetex, SongParser

from generator.models import Song, Artist

import re
import os
import sys
import pprint
import logging

LOGGER = logging.getLogger(__name__)

class Renderer:
    def __init__(self, document):
        self.document = document
        self._render = {
                '#text': self.renderText,
                'verse': self.renderVerse,
                'verse*': self.renderVerse,
                'chorus': self.renderVerse,
                'bridge': self.renderVerse,
                'par': self.renderPar,
                'chord': self.renderChord,
                'active::\n': self.renderPlainText(u"<br>"),
                'dots': self.renderPlainText(u"…"),
                }
        self._render_text = {}

    def renderNodes(self, nodes):
        return "".join([
            self._render.get(
                node.nodeName,
                self.renderDefault
                )(node)
            for node in nodes
            ])


    def renderDefault(self, node):
        print("TODO Default for", unicode(node), node.nodeName)
        return u""

    def renderPlainText(self, string):
        def __renderPlainText(__):
            return string
        return __renderPlainText

    def renderText(self, node):
        return self._render_text.get(
                unicode(node),
                self.renderPlainText(unicode(node)),
                )(node)

    def renderVerse(self, node):
        res = ""
        res += "<p class={}>\n".format(node.nodeName.replace('*', '_star'))
        res += self.renderNodes(node.childNodes)
        res += "</p>"
        return res

    def renderPar(self, node):
        # TODO
        return ""

    def renderChord(self, node):
        # TODO Remplacer par un with
        self._render.update({
            'active::&': self.renderPlainText(u"♭"),
            })
        self._render_text.update({
            '#': self.renderPlainText(u"♯"),
            })
        return u"""<span class="chord">
                 <span class="chord-name">
                 {}
                 </span><span class="chord-text">
                 {}
                 </span>
                 </span>""".format(
                         self.renderNodes(node.childNodes),
                         "", # TODO
                         )


def parse_song(filename):
    tex = SongParser.parse(filename)
    return Renderer(tex).renderNodes(tex.childNodes)

def import_song(repo, filepath):
    '''Import a song in the database'''
    data = parsetex(filepath)
    LOGGER.info("Processing " + 
                pprint.pformat(data['titles'][0]))

    artist_name = smart_text(data['args']['by'], 'utf-8')
    artist_slug = slugify(artist_name)

    artist_model, created = Artist.objects.get_or_create(
                            slug=artist_slug,
                            defaults={'name': artist_name}
                            )
    if not created:
        if (artist_model.name != artist_name):
            LOGGER.warning(
                "*** Artist name differs though "
                "slugs are equal : "
                + artist_name + " / "
                + artist_model.name)

    if (len(data['languages']) > 1):
        LOGGER.warning("*** Multiple languages "
                        "in song file; we though"
                        " only support one. "
                        "Picking any.")
    if (len(data['languages']) > 0):
        language_name = data["languages"].pop()
        language_code = next(
                    (x for x in LANGUAGES
                     if x[1].lower() == language_name.lower()
                     ),
                    ('', '')
                     )[0]
        if language_code == '':
            LOGGER.warning("*** No code found for "
                    "language : '" + language_name + "'")

    song_title = smart_text(data['titles'][0], 'utf-8')
    song_slug = slugify(song_title)

    object_hash = repo.git.hash_object(filepath)
    SONG_DIR = os.path.join(repo.working_dir, "songs")
    filepath_rel = os.path.relpath(filepath, SONG_DIR)

    import random

    # For some reason - probably after having interrupted
    # the generation - insertion fails because slug is
    # empty, and there is already an empty one.
    # We assign here a random value, that gets overwritten
    # afterwards.
    song_model, created = Song.objects.get_or_create(
                            title=song_title,
                            artist=artist_model,
                            defaults={
                            'title': song_title,
                            'language': language_code,
                            'file_path': filepath_rel,
                            'slug': ('%06x' % random.randrange(16**6)) })
    if created:
        if Song.objects.filter(slug=song_slug).exists():
            song_slug += '-' + str(song_model.id)
        song_model.slug = song_slug

    else:
        LOGGER.info("-> Already exists.")

    artist_model.save()
    song_model.object_hash = object_hash
    song_model.save()
