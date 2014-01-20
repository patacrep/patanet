# -*- coding: utf-8 -*-

# A supprimer en prod.
from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import patterns, url ,include
from generator.views import SongView, SongListByArtist, ArtistList, view_profile, PasswordChange, PasswordReset#, Register

urlpatterns = patterns('generator.views',
    url(r'^$', 'home', name="home"),
    url(r'^songs/(?P<artist>.+)/$', SongListByArtist.as_view(), name="song_list_by_artist"),
    url(r'^songs/(?P<artist>.+)/(?P<slug>.+)/$', SongView.as_view(), name='show_song'),
    url(r'^songs/$', ArtistList.as_view(), name="artist_list"),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^user/$',view_profile, name='profil'),
    url(r'^user/login$','login',{'template_name': 'generator/login.html'}, name='login'),
    url(r'^user/logout$', 'logout',{'next_page': '/'}, name='logout'),
    url(r'^user/change-password$', PasswordChange.as_view(),name='password_change'),
    url(r'^user/reset-password$', PasswordReset.as_view(),name='password_reset'),
    url(r'^user/reset-password-do?uid=(?P<uidb36>.+)&token=(?P<token>.+)$', PasswordReset.as_view(),name='password_reset_confirm'),
#    url(r'^user/register$', Register.as_view(),name='register'),
)

urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)