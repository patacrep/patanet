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
 Template file for settings that should override or complete entries
 in settings.py on your configuration.

 ONLY EDIT AS A TEMPLATE for creating a local_settings.py file !
 This template file is *not* included during execution. Only
 local_settings.py is.

 See settings.py for more information about each value.
"""

# import os
# from django.conf import settings

'''
Runtime settings
'''
# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = "SomeThingLongAndComplicated@@##//r!"

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
# TEMPLATE_DEBUG = True
# ALLOWED_HOSTS = []

'''
Administrators
'''

# ADMINS = (('Your Name','Your email address'))
#
# DEFAULT_FROM_EMAIL = '' # webmaster@nom.du.site
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025


'''
Databases
'''

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(settings.PROJECT_ROOT, 'db.sqlite3'),
#         'USER':'',
#         'PASSWORD':'',
#         'HOST':'',
#         'PORT':'',
#     }
# }

'''
Search paths
'''
# Path to the songs directory (*.sg files) from the songbook repo
# SONGS_LIBRARY_DIR = os.path.join(settings.PROJECT_ROOT, '../songbook-data/')


'''
PDF cleaning settings
'''
# from datetime import timedelta
# SONGBOOK_DELETE_POLICY = {"mode": "time",  or "user" or "total_number"
#                          "expiration_time": timedelta(weeks=1),
#                          "number": -1
#                          }
