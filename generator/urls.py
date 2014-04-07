# -*- coding: utf-8 -*-

# A supprimer en prod.
from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import patterns, url
from generator.views import SongList, SongView, SongListByArtist, ArtistList, \
     view_profile, PasswordChange, Register, contact, \
     NewSongbook, ShowSongbook, SongbookPublicList, SongbookPrivateList, \
     UpdateSongbook, DeleteSongbook,\
     reset_password, reset_password_confirm, password_reset_done, \
     password_reset_complete, ItemsListInSongbook, move_or_delete_items,\
    FlatPage
from django.views.generic.base import TemplateView

urlpatterns = patterns('generator.views',
    url(r'^$', FlatPage.as_view(url='home'), name="home"),
    url(r'^songs/(?P<artist>[\w-]+)/(?P<slug>[\w-]+)/$',
                SongView.as_view(),
                name='show_song'),
    #url(r'^songs/(?P<artist>[\w-]+)/(?P<slug>[\w-]+)/edit$',
                # MISSING_VIEW,
                # name='edit_song'),
    #url(r'^songs/(?P<artist>[\w-]+)/(?P<slug>[\w-]+)/history$',
                # MISSING_VIEW,
                # name='song_history'),
    url(r'^songs/(?P<artist>[\w-]+)/$',
                SongListByArtist.as_view(),
                name="song_list_by_artist"),
    url(r'^songs/$',
                SongList.as_view(),
                name="song_list"),
    url(r'^songs/random$',
                'random_song',
                name="random_song"),
    #url(r'^songs/search', MISSING_VIEW, name="song_search"),
    url(r'^artists/$',
                ArtistList.as_view(),
                name="artist_list"),

    url(r'^songbooks/$',
                SongbookPublicList.as_view(),
                name="songbook_list"),
    url(r'^songbooks/my/$',
                SongbookPrivateList.as_view(),
                name="songbook_private_list"),
    url(r'^songbooks/(?P<id>\d+)-(?P<slug>[\w-]+)/$',
                ShowSongbook.as_view(),
                name="show_songbook"),
    url(r'^songbooks/(?P<id>\d+)-(?P<slug>[\w-]+)/songs$',
                ItemsListInSongbook.as_view(),
                name="item_list"),
    url(r'^songbooks/(?P<id>\d+)-(?P<slug>[\w-]+)/change$',
                move_or_delete_items,
                name="change_item_list"),
    url(r'^songbooks/(?P<id>\d+)-(?P<slug>[\w-]+)/edit$',
                UpdateSongbook.as_view(),
                name="edit_songbook"),
    url(r'^songbooks/(?P<id>\d+)-(?P<slug>[\w-]+)/delete',
                DeleteSongbook.as_view(),
                name="delete_songbook"),
    url(r'^songbooks/new$',
                NewSongbook.as_view(),
                name="new_songbook"),
    url(r'^songbooks/set$',
                'set_current_songbook',
                name="set_current_songbook"),
    url(r'^songbooks/add-song$',
                'add_songs_to_songbook',
                name='add_song_to_songbook'),
    url(r'^songbooks/(?P<id>\d+)-(?P<slug>[\w-]+)/render',
                'render_songbook',
                name="render_songbook"),

)

urlpatterns += patterns('',
    url(r'^contact/$',
                contact,
                name='contact'),
    url(r'^user/$',
                view_profile,
                name='profile'),
    url(r'^user/login$',
                'django.contrib.auth.views.login',
                {'template_name': 'generator/login.html'},
                name='login'),
    url(r'^user/logout$',
                'django.contrib.auth.views.logout',
                {'next_page': '/'},
                name='logout'),
    url(r'^denied$',
                TemplateView.as_view(template_name="generator/denied.html"),
                name="denied"),
    url(r'^user/change-password$',
                PasswordChange.as_view(),
                name='password_change'),
    url(r'^user/reset-password$',
                reset_password,
                name='password_reset'),
    url(r'^user/reset-password-done$',
                password_reset_done,
                name='password_reset_done'),
    url(r'^user/reset-password-do/(?P<uidb64>.+)/(?P<token>.+)/$',
                reset_password_confirm,
                name='password_reset_confirm'),
    url(r'^user/reset-password-complete$',
                password_reset_complete,
                name='password_reset_complete'),
    url(r'^user/register$',
                Register.as_view(),
                name='register'),
    #url(r'^user/edit',
            # MISSING_VIEW,
            # name='profile_edit'),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
