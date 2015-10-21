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


from django import template

from generator.views.utils import letter_page
from generator.forms import latex_free_attributes as latex_free_dict

## Template filters
##############################################
register = template.Library()

@register.filter
def first_letter(name):
    return letter_page(name)

@register.filter
def intersection_id(objects, ids):
    object_ids = [obj.id for obj in objects]
    return set.intersection(set(ids), set(object_ids))

@register.filter
def search_image(image, song):
    """Get the path to an image file (or None if not found)"""
    if not image:
        return None
    arg = image.argument
    return song.search_image(image.argument)

## Template tags
##############################################

@register.simple_tag
def latex_free_attributes():
    attributes = latex_free_dict()
    attr = ' '.join("{}='{!s}'".format(key,val) for (key,val) in attributes.items())
    return attr
