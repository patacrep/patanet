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
