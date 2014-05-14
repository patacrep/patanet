# -*- coding: utf-8 -*-
# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt

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
