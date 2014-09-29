# -*- coding: utf-8 -*-
# Adaptated from 
# http://effbot.org/zone/django-multihost.htm

"""
A simple middleware component that lets you use a single Django
instance to server multiple distinct hosts.
"""

from django.conf import settings
from django.utils.cache import patch_vary_headers

class MultiHostMiddleware:

    def process_request(self, request):
        try:
            host = request.META["HTTP_HOST"]
            try:
                host, port = host.split(':')
            except ValueError:
                pass # No port value in request.META["HTTP_HOST"]
            request.urlconf = settings.MULTIHOSTS_URLCONF[host]
        except KeyError:
            pass # use default urlconf (settings.ROOT_URLCONF)

    def process_response(self, request, response):
        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))
        return response

# Set differents errors views using 
# handler404 = "mydjango.app.company_view.handler404"
# handler500 = "mydjango.app.company_view.handler500"
# in url file