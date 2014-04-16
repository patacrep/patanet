# -*- coding: utf-8 -*-
# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt


from django import template

## Template filters
##############################################
register = template.Library()

@register.filter(name='in')
def in_queryset(value, arg):
    return value in arg

@register.filter(name='in_subitem')
def in_subitem(value, arg):
    for item in arg:
        if item.item == value :
            return True
    return False
