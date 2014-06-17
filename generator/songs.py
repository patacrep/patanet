# -*- coding: utf-8 -*-
#    Copyright (C) 2014 The Songbook Team
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

from songbook_core.plastex import parsetex, SongParser

from generator.models import Song, Artist

import re
import os
import sys
import pprint

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
                }

    def renderNodes(self, nodes):
        return "".join([
            self._render.get(node.nodeName, self.renderDefault)(node)
            for node in nodes
            ])

    def renderDefault(self, node):
        if getattr(node, 'tagName', None) == 'active::\n':
            return "<br>"
        else:
            print("TODO Default for", unicode(node))
            return ""

    def renderText(self, node):
        return unicode(node)

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
        # Je ne comprend pas pourquoi la version suivante, bien plus élégante,
        # m'introduit des saut de ligne partout...
        # return u"""<span class="chord">
        #         <span class="chord-name">
        #         {}
        #         </span><span class="chord-text">
        #         {}
        #         </span>
        #         </span>""".format(
        #                 node.chord.replace('&', u"♭").replace('#', u"♯"),
        #                 "", # TODO
        #                 )
        return (
                u'<span class="chord">'
                u'<span class="chord-name">'
                u'{}'
                u'</span><span class="chord-text">'
                u'{}'
                u'</span>'
                u'</span>'
                ).format(
                        node.chord.replace('&', u"♭").replace('#', u"♯"),
                        "", # TODO
                        )


def parse_song(filename):
    tex = SongParser.parse(filename)
    return Renderer(tex).renderNodes(tex.childNodes)


# TODO: Write all the output to a log file
def import_song(repo, filepath):
    '''Import a song in the database'''
    data = parsetex(filepath)
    sys.stdout.write("Processing " +
                      pprint.pformat(data['titles'][0]))

    artist_name = smart_text(data['args']['by'], 'utf-8')
    artist_slug = slugify(artist_name)

    artist_model, created = Artist.objects.get_or_create(
                            slug=artist_slug,
                            defaults={'name': artist_name}
                            )
    if not created:
        if (artist_model.name != artist_name):
            sys.stderr.write(
                "*** Artist name differs though "
                "slugs are equal : "
                + artist_name + " / "
                + artist_model.name)

    if (len(data['languages']) > 1):
        sys.stderr.write("*** Multiple languages " +
                          "in song file; we though" +
                          " only support one. " +
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
            sys.stderr.write("*** No code found for "
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
        sys.stdout.write("-> Already exists.")

    artist_model.save()
    song_model.object_hash = object_hash
    song_model.save()
