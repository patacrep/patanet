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
