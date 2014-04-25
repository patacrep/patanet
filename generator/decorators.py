# -*- coding: utf-8 -*-
# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt


from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from functools import wraps

from generator.models import Songbook, ItemsInSongbook


class CurrentSongbookMixin(object):
    '''
    Mixin addding the current songbook from the sessions in the context data.
    '''

    def get_context_data(self, **kwargs):
        context = super(CurrentSongbookMixin, self).get_context_data(**kwargs)
        context['show_current_songbook'] = True
        try:
            songbook = Songbook.objects.get(
                            id=self.request.session['current_songbook'])
            context['current_songbook'] = songbook
            current_item_list = ItemsInSongbook.objects.filter(
                                                    songbook=songbook)
            context['current_item_list'] = current_item_list

            if songbook.count_section() > 1:
                context['multi_section'] = True
                context['first_section'] = current_item_list.filter(
                                            item_type__model='section')[0]
            if songbook.count_section() > 0:
                context['sb_has_section'] = True

        except (KeyError, Songbook.DoesNotExist):
            pass
        return context


def _get_songbook(lookups, **kwargs):
    model = Songbook
    # Parse lookups
    if len(lookups) % 2 != 0:
        raise ImproperlyConfigured(
            "Lookup variables must be provided "
            "as pairs of lookup_string and view_arg")
    lookup_dict = {}
    for lookup, view_arg in zip(lookups[::2], lookups[1::2]):
        if view_arg not in kwargs:
            raise ImproperlyConfigured(
                "Argument %s was not passed "
                "into view function" % view_arg)
        lookup_dict[lookup] = kwargs[view_arg]
    return get_object_or_404(model, **lookup_dict)


def owner_required(lookups=None, instance=None, **kwargs):
    """
    Decorator for views that checks whether a user can see a songbook.
    The songbook can only be seen if the user own it.
    Adaptated from the django-guardian decorator @permission_required
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            songbook = None
            if lookups:
                songbook = _get_songbook(lookups, **kwargs)
            elif instance:
                songbook = instance

            if not songbook.user.user == request.user:
                return redirect(reverse('denied'))
            return view_func(request, *args, **kwargs)
        return wraps(view_func)(_wrapped_view)
    return decorator


def owner_or_public_required(lookups=None, **kwargs):
    """
    Decorator for views that checks whether a user can see a songbook.
    The songbook can be seen if it is public or if the user own it.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            songbook = None
            if lookups:
                songbook = _get_songbook(lookups, **kwargs)

            if songbook.is_public:
                return view_func(request, *args, **kwargs)
            else:
                return owner_required(instance=songbook)(view_func
                                    )(request, *args, **kwargs)
        return wraps(view_func)(_wrapped_view)
    return decorator

# # Some mixins for view acess
#################################


class LoginRequiredMixin(object):
    '''View mixin checking if the user is logged in'''

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class OwnerRequiredMixin(object):
    '''View mixin checking if the user has
    the permission to see the songbook'''

    @method_decorator(owner_required(('id', 'id')))
    def dispatch(self, *args, **kwargs):
        return super(OwnerRequiredMixin, self).dispatch(*args, **kwargs)


class OwnerOrPublicRequiredMixin(object):
    '''View mixin checking if the user has
    the permission to see the songbook'''

    @method_decorator(owner_or_public_required(('id', 'id')))
    def dispatch(self, *args, **kwargs):
        return super(OwnerOrPublicRequiredMixin, self).dispatch(*args, **kwargs)