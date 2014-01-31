from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.conf.urls.i18n import i18n_patterns

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    )

urlpatterns += i18n_patterns('',
    url(r'',include('generator.urls')),
    )
