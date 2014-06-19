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

from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns

from django.contrib import admin
admin.autodiscover()

from generator.views import FlatPage

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    )

urlpatterns += i18n_patterns('',
    url(r'', include('generator.urls')),
    )

urlpatterns += i18n_patterns('',
    url(r'^pages/(?P<url>[\w-]+)', FlatPage.as_view(), name="flatpage"),
    )


from django.conf import settings
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^medias/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}
            ),
        url(r'^data/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT}
            )
    )
