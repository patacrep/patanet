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
Staticfiles storage compiling the .less files into css when collectstatic
is called.
"""
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.conf import settings
from lesscpy.lessc import parser, formatter

import os


CSS_FILES = [os.path.join("css", "main"),
              os.path.join("css", "normalize"),
              ]

LESS_FILES = [ filename + ".less" for filename in CSS_FILES ]

class LessCompileStorage(StaticFilesStorage):

    def post_process(self, paths, dry_run=True, **kwargs):
        '''Post-process files by checking if they should be compiled into css.'''
        for original_path in paths.keys():
            if original_path in LESS_FILES:
                processed, processed_path = compile_less_file(original_path,
                                                              dry_run)
            else:
                processed_path = original_path
                processed = False

            yield original_path, processed_path, processed


def compile_less_file(filename_in, dry_run=True):
    ext = filename_in.split('.')[-1]
    filename = filename_in[: -(len(ext) + 1)]
    if not ext.lower() == "less":
        return False, filename_in

    filename_in = os.path.join(settings.STATIC_ROOT,
                                filename_in)
    filename_out = os.path.join(settings.STATIC_ROOT,
                                filename) + ".css"

    compile_less(filename_in, filename_out, dry_run)
    return True, filename_out


class FormatterArgs(object):
    """Class for pasing args to the CSS formatter"""
    def __init__(self):
        self.xminify = True


def compile_less(filename_in, filename_out, dry_run=True):
    """Compile a less file to css and write it to a file"""
    p = parser.LessParser(yacc_debug=False,
                          lex_optimize=True,
                          yacc_optimize=True,
                          scope=None,
                          tabfile=None,
                          verbose=False)
    p.parse(filename=filename_in, debuglevel=0)
    args = FormatterArgs()
    f = formatter.Formatter(args)
    css = f.format(p)
    if not dry_run:
        with open(filename_out, 'w') as outfile:
            outfile.write(css)
