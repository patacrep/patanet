# -*- coding: utf-8 -*-

# A supprimer en prod.
from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import patterns, url ,include
from generator.views import AfficherChant, ListeChantsParAuteur, ListeAuteurs, view_profile

urlpatterns = patterns('generator.views',
    url(r'^$', 'home', name="home"),
    url(r'^message:(?P<message>.+)','show_message'),             
    url(r'^songs/(?P<chanteur>.+)/$', ListeChantsParAuteur.as_view(), name="song_list_by_artist"),
    url(r'^songs/(?P<chanteur>.+)/(?P<slug>.+)/$', AfficherChant.as_view(), name='show_song'),
    url(r'^songs/$', ListeAuteurs.as_view(), name="artist_list"),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^user/$',view_profile, name='profil'),
    url(r'^user/login$','login',{'template_name': 'generator/login.html'}, name='login'),
    url(r'^user/logout/$', 'logout',{'next_page': '/'}, name='logout'),
    url(r'^user/change-password$', 'password_change',
            {'template_name':'generator/password_change.html',
             'post_change_redirect':'/message:pswd-changed'
             },
            name='password_change'
        ),
    url(r'^user/reset-password$', 'password_reset', 
        {'template_name':'generator/reset_password.html',
         'email_template_name':'generator/reset_password_email.html', # TODO:  Améliorer le template
         'subject_template_name':'Demande de réinitialisation de mot de passe', # TODO: Améliorer le sujet
         'post_reset_redirect':'/message:pswd-reset-ask'}, 
        name='reset_password'),     
)

urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)