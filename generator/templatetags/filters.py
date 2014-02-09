# -*- coding: utf-8 -*-

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
