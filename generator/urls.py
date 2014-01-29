# -*- coding: utf-8 -*-

# A supprimer en prod.
from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import patterns, url
from generator.views import SongList, SongView, SongListByArtist, ArtistList, \
     view_profile, PasswordChange, PasswordReset, Register, \
     NewSongbook, ShowSongbook, SongbookList

urlpatterns = patterns('generator.views',
    url(r'^$', 'home', name="home"),
    url(r'^songs/(?P<artist>[\w-]+)/(?P<slug>[\w-]+)/$', SongView.as_view(), name='show_song'),
    #url(r'^songs/(?P<artist>[\w-]+)/(?P<slug>[\w-]+)/edit$', MISSING_VIEW, name='edit_song'),
    #url(r'^songs/(?P<artist>[\w-]+)/(?P<slug>[\w-]+)/history$', MISSING_VIEW, name='song_history'),
    url(r'^songs/(?P<artist>[\w-]+)/$', SongListByArtist.as_view(), name="song_list_by_artist"),
    url(r'^songs/$', SongList.as_view(), name="song_list"),
    #url(r'^songs/random$', MISSING_VIEW, name="random_song"),
    #url(r'^songs/search', MISSING_VIEW, name="song_search"),
    url(r'^artists/$', ArtistList.as_view(), name="artist_list"),
    
    url(r'^songbooks/$', SongbookList.as_view(), name="songbook_list"),
    url(r'^songbooks/(?P<pk>\d+)-(?P<slug>[\w-]+)/$', ShowSongbook.as_view(), name="show_songbook"),
    #url(r'^songbooks/(?P<pk>\d+)-(?P<slug>[\w-]+)/songs$', MISSING_VIEW, name=""),
    #url(r'^songbooks/(?P<pk>\d+)-(?P<slug>[\w-]+)/edit$', MISSING_VIEW, name=""),
    url(r'^songbooks/new$', NewSongbook.as_view(), name="new_songbook"),
    url(r'^songbooks/add-song$', 'add_song_to_songbook', name='add_song_to_songbook'),
)

urlpatterns += patterns('',
    url(r'^user/$',view_profile, name='profile'),
    url(r'^user/login$','django.contrib.auth.views.login',{'template_name': 'generator/login.html'}, name='login'),
    url(r'^user/logout$', 'django.contrib.auth.views.logout',{'next_page': '/'}, name='logout'),
    url(r'^user/change-password$', PasswordChange.as_view(),name='password_change'),
    url(r'^user/reset-password$', PasswordReset.as_view(),name='password_reset'),
    url(r'^user/reset-password-do$', PasswordReset.as_view(),name='password_reset_confirm'),
    url(r'^user/register$', Register.as_view(),name='register'),
    #url(r'^user/edit', MISSING_VIEW,name='profile_edit'),
)

urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)