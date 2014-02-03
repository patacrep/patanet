# -*- coding: utf-8 -*-

from django import template

## Template filters
##############################################
register = template.Library()

@register.filter(name='in')
def in_queryset(value, arg):
    return value in arg
