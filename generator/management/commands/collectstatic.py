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
Custom collectstatic command, compiling LESS files to CSS.
"""

import django.contrib.staticfiles.management.commands.collectstatic as CS
from django.conf import settings

from lesscpy.lessc import parser, lexer, formatter

import os
import sys

LESS_FILES = [os.path.join(settings.STATIC_ROOT, "css", "main"),
              os.path.join(settings.STATIC_ROOT, "css", "normalize"),
              ]


class FormatterArgs(object):
    """Class for pasing args to the CSS formatter"""
    def __init__(self):
        self.xminify = True


def compile_less(infile, outf, dry_run=False):
    """Compile a less file to css and write it to a file"""
    p = parser.LessParser(yacc_debug=False,
                          lex_optimize=True,
                          yacc_optimize=True,
                          scope=None,
                          tabfile=None,
                          verbose=False)
    p.parse(filename=infile, debuglevel=0)
    args = FormatterArgs()
    f = formatter.Formatter(args)
    css = f.format(p)
    if not dry_run:
        with open(outf, 'w') as outfile:
            outfile.write(css)


class Command(CS.Command):

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        sys.stdout.write("Compiling LESS files\n")
        for less_file in LESS_FILES:
            compile_less(less_file + ".less",
                         less_file + ".css",
                         dry_run=False)
