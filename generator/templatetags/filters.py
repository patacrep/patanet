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

@register.filter(name='list_in_items')
def list_in_items(value, arg):
    items = [item.item for item in arg]
    values = [val for val in value]
    return set(values).issubset(set(items))

@register.filter(name='in_items')
def in_items(value, arg):
    items = [item.item for item in arg]
    return value in items
