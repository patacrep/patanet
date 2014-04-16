# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt

"""
WSGI config for Songbook_web project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os, sys
sys.path.append('/home/songbook-web/www/songbook-web')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Songbook_web.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
