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

from django.template import TemplateSyntaxError, Node, Variable, Library
from django.conf import settings

register = Library()


@register.tag
def settings(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'{name}' takes at least one "
                                  "argument (settings constant to retrieve)"
                                  .format(name=bits[0]))
    settingsvar = bits[1]
    settingsvar = settingsvar[1:-1] if settingsvar[0] == '"' else settingsvar
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]
    if len(bits):
        raise TemplateSyntaxError("'settings' didn't recognise "
                                  "the arguments '%s'" % ", ".join(bits))
    return ValueFromSettings(settingsvar, asvar)


class ValueFromSettings(Node):

    def __init__(self, settingsvar, asvar):
        self.arg = Variable(settingsvar)
        self.asvar = asvar

    def render(self, context):
        ret_val = getattr(settings, str(self.arg))
        if self.asvar:
            context[self.asvar] = ret_val
            return ''
        else:
            return ret_val

