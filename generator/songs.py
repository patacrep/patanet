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
Functions for song file (.sg) rendering.
"""
from patacrep.plastex import parsetex

import re
import os
import sys
import pprint
import logging

from contextlib import contextmanager

LOGGER = logging.getLogger(__name__)

class Renderer(object):
    """Render a PlasTeX-parsed song as HTML"""

    def __init__(self, song):
        self.song = song
        self.document = song['_doc']
        self._render = {
                '#text': self.render_text,
                'verse': self.render_verse,
                'verse*': self.render_verse,
                'chorus': self.render_verse,
                'bridge': self.render_verse,
                'par': self.render_par,
                'chord': self.render_chord,
                'active::\n': self.render_plain_text(u"<br>"),
                'selectlanguage': self.render_silent,
                'songcolumns': self.render_silent,
                'beginsong': self.render_silent,
                'endsong': self.render_silent,
                'cover': self.render_silent,
                #'gtab': self.render_gtab,
                'gtab': self.render_silent,
                'bgroup': self.render_group,
                }
        self._render_text = {}

    @contextmanager
    def push(self, attr, extension):
        """With statement used to locally update a dictonary

        Arguments:
        - attr: name (as a string) of the attribute to update. `self.attr`
          must be a dictonary.
        - extension: dictionary to use to update the dictonary.
        """
        old = dict(getattr(self, attr))
        getattr(self, attr).update(extension)
        yield
        setattr(self, attr, old)

    def render(self):
        """Return the HTML version of self."""
        return self.render_nodes(self.document.childNodes)

    @staticmethod
    def render_plain_text(string):
        """Return a `render_*`-like function that return a constant string."""
        def _render_plain_text(__node):
            """Return constant string."""
            return string
        return _render_plain_text

    def render_nodes(self, nodes):
        """Render a list of nodes"""
        return u"".join([
            self._render.get(
                node.nodeName,
                self.render_default
                )(node)
            for node in nodes
            ])

    @staticmethod
    def render_default(node):
        """Default rendering of a node

        - If `node` has an attribute `unicode`, return
          `node.unicode`.
        - Otherwise, return `node.textContent`.
        """
        if hasattr(node, 'unicode'):
            if isinstance(node.unicode, basestring):
                return node.unicode

        LOGGER.warning(u"Cannot render node {} (type: {}; name: {})".format(
            node,
            type(node),
            node.nodeName,
            ))
        if isinstance(node.textContent, basestring):
            return node.textContent
        else:
            return u""

    @staticmethod
    def render_silent(_):
        """Return nothing

        To be used by LaTeX commands that does not produce any output.
        """
        return u""

    def render_group(self, node):
        return self.render_nodes(node.childNodes)

    @staticmethod
    def render_gtab(node):
        r"""Render LaTeX `\gtab` command."""
        return u"GTAB({chord}, {diagram})".format(
                diagram=node.attributes["diagram"],
                chord=node.attributes["chord"],
                )

    def render_text(self, node):
        """Render a text node.

        - If `unicode(node)` is a key of `self._render_text`, return
          `self._render_text[unicode(node)](node)`.
        - Otherwise, return `self.render_default(node)`.
        """
        return self._render_text.get(
                unicode(node),
                self.render_default,
                )(node)

    def render_verse(self, node):
        """Render a `verse`, `verse*` or `chorus` environment."""
        res = u""
        res += u"<p class=\"{}\">".format(node.nodeName.replace('*', '_star'))
        res += self.render_nodes(node.childNodes)
        res += u"</p>"
        return res

    @staticmethod
    def render_par(__node):
        """Render a paragraph."""
        # TODO
        return u""

    def render_chord(self, node):
        r"""Render a chord command `\[`."""
        with self.push("_render", {'active::&': self.render_plain_text(u"♭")}):
            with self.push("_render_text", {'#': self.render_plain_text(u"♯")}):
                name = self.render_nodes(node.attributes["name"])
        text = self.render_nodes(node.childNodes)
        return (u'<span class="chord">'
                u'<span class="chord-name">'
                u'{name}'
                u'</span><span class="chord-text">'
                u'{text}'
                u'</span>'
                u'</span>').format(name=name, text=text)


def parse_song(filename):
    """Parse song 'filename', and return the corresponding HTML code."""
    song = parsetex(filename)
    return Renderer(song).render()
