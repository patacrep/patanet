# -*- coding: utf-8 -*-
# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt


from django.contrib import messages
from django import template
from django.http.response import Http404
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, \
                                UpdateView, FormView, TemplateView

from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.core.mail.message import BadHeaderError

##############################################

from generator.models import Song, Artist, Songbook, Profile, \
                            ItemsInSongbook, \
                            Task as GeneratorTask, Layout
from generator.forms import RegisterForm, SongbookCreationForm, ContactForm
from generator.name_paginator import NamePaginator
from django.views.generic.edit import DeleteView
from django.contrib.auth.views import password_reset, password_reset_confirm
from generator.decorators import CurrentSongbookMixin, \
    OwnerRequiredMixin, LoginRequiredMixin, owner_required, \
    OwnerOrPublicRequiredMixin
from generator.songs import parse_song

from Songbook_web.settings import SONGS_LIBRARY_DIR

import os
##############################################
##############################################


class FlatPage(TemplateView):
    '''Class handling all the static pages of the app,
    like 'about' or 'FAQ'.
    It try to get and render a template located in 'generator/pages/<url>.html'
    '''
    url = None

    def get_template_names(self):
        try:
            url = self.kwargs['url']
        except KeyError:
            url = str(self.url)
        template_name = 'generator/pages/' + url + '.html'
        try:
            template.loader.get_template(template_name)
            return template_name
        except template.TemplateDoesNotExist:
            raise Http404


def home(request):
    headertitle = _(u'Accueil')
    return render(request, 'generator/home.html', locals())


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            username = None
            if request.user.is_authenticated():
                username = request.user.username
            try:
                form.send_mail(username)
                messages.success(request,
                                 _(u"Votre message a bien été envoyé."))
            except BadHeaderError:
                messages.error(request,
                               _(u"Erreur d'en-tête. Vérifiez le sujet."))
                return render(request, 'generator/contact.html', locals())
            except:
                messages.error(request,
                               _(u"Une erreur s'est produite. Veuillez réessayer."))
                return render(request, 'generator/contact.html', locals())
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'generator/contact.html', locals())

# # User specifics views
##############################################


@login_required
def view_profile(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'generator/show_profile.html', locals())


class Register(CreateView):
    template_name = 'generator/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, _(u"Vous êtes à présent inscrit."
                    u"Connectez-vous pour accéder à votre profil."))
        return super(Register, self).form_valid(form)


class PasswordChange(LoginRequiredMixin, FormView):
    template_name = 'generator/password_change.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('profile')

    def get_form_kwargs(self):
        kwargs = super(PasswordChange, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request,
                         _(u"Votre mot de passe a bien été modifié.")
                         )
        return super(PasswordChange, self).form_valid(form)


def reset_password(request):
    """A wrapper function for password reset"""
    return password_reset(request,
        template_name='generator/password_reset.html',
        email_template_name='generator/password_reset_email.html',
        subject_template_name='generator/password_reset_email_subject.txt',
        post_reset_redirect=reverse('password_reset_done'))


def password_reset_done(request):
    """Only add a message and redirect to home"""
    messages.success(request, _(u"Un email de confirmation vous a été envoyé."))
    return redirect(reverse('home'))


def reset_password_confirm(request, uidb64, token):
    """A wrapper function for password reset confirmation"""
    return  password_reset_confirm(request,
                    uidb64=uidb64,
                    token=token,
                    template_name='generator/password_reset_confirm.html',
                    post_reset_redirect=reverse('password_reset_complete'),
                    extra_context={'uid': uidb64, 'token': token})


def password_reset_complete(request):
    """Only add a message and redirect to home"""
    messages.success(request, _(u"Votre mot de passe a bien été modifié. "
                                u"Connectez-vous pour accéder à votre profil."))
    return redirect(reverse('home'))

# # Songs views
##############################################


class SongList(CurrentSongbookMixin, ListView):
    model = Song
    context_object_name = "song_list"
    template_name = "generator/song_list.html"
    paginate_by = 10
    paginator_class = NamePaginator
    queryset = Song.objects.all().order_by('slug')


class SongListByArtist(CurrentSongbookMixin, ListView):
    model = Song
    context_object_name = "song_list"
    template_name = "generator/song_list_by_artist.html"
    paginate_by = 10

    def get_queryset(self):
        self.artist = get_object_or_404(Artist, slug=self.kwargs['artist'])
        return Song.objects.filter(artist=self.artist).order_by('slug')

    def get_context_data(self, **kwargs):
        context = super(SongListByArtist, self).get_context_data(**kwargs)
        context['artist'] = Artist.objects.get(slug=self.kwargs['artist'])
        return context


def _read_song(song):
    path = os.path.join(SONGS_LIBRARY_DIR, 'songs', song.file_path)
    with open(path, 'r') as song_file:
        content = song_file.read()
    return parse_song(content)


class SongView(CurrentSongbookMixin, DetailView):
    context_object_name = "song"
    model = Song
    template_name = "generator/show_song.html"

    def get_queryset(self):
        return Song.objects.filter(
                        artist__slug=self.kwargs['artist'],
                        slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(SongView, self).get_context_data(**kwargs)
        context['content'] = _read_song(context['song'])
        return context


class ArtistList(CurrentSongbookMixin, ListView):
    model = Artist
    context_object_name = "artist_list"
    template_name = "generator/artist_list.html"
    paginate_by = 10
    paginator_class = NamePaginator
    queryset = Artist.objects.order_by('slug')


def random_song(request):
    song = Song.objects.order_by('?')[0]
    return redirect(reverse('show_song',
                            kwargs={'artist': song.artist.slug,
                                    'slug': song.slug}
                            ))

# # Songbooks views
##############################################


class SongbookPublicList(ListView):
    model = Songbook
    context_object_name = "songbooks"
    template_name = "generator/songbook_public_list.html"

    def get_queryset(self):
        return Songbook.objects.filter(is_public=True
                                       ).order_by('title')


class SongbookPrivateList(ListView):
    model = Songbook
    context_object_name = "songbooks"
    template_name = "generator/songbook_private_list.html"

    def get_queryset(self):
        return Songbook.objects.filter(user__user=self.request.user
                                       ).order_by('title')


class NewSongbook(LoginRequiredMixin, CreateView):
    model = Songbook
    template_name = 'generator/new_songbook.html'
    form_class = SongbookCreationForm
    success_url = reverse_lazy('songbook_private_list')

    def form_valid(self, form):
        form.user = self.request.user
        messages.success(self.request, _(u"Le nouveau carnet a été créé."))
        return super(NewSongbook, self).form_valid(form)


class ShowSongbook(OwnerOrPublicRequiredMixin, DetailView):
    model = Songbook
    template_name = 'generator/show_songbook.html'
    context_object_name = 'songbook'

    def get_queryset(self):
        return Songbook.objects.filter(id=self.kwargs['id'],
                                       slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(ShowSongbook, self).get_context_data(**kwargs)
        item_list = ItemsInSongbook.objects.filter(songbook=self.object)
        context['item_list'] = item_list
        if self.request.user == self.object.user.user:
            context['can_edit'] = True
        else:
            context['can_edit'] = False
        return context


class UpdateSongbook(OwnerRequiredMixin, UpdateView):
    model = Songbook
    template_name = 'generator/update_songbook.html'
    form_class = SongbookCreationForm

    def get_success_url(self):
        self.kwargs["slug"] = self.object.slug
        return reverse('show_songbook', kwargs=self.kwargs)

    def form_valid(self, form):
        form.user = self.request.user
        messages.success(self.request, _(u"Le carnet a été modifié."))
        return super(UpdateSongbook, self).form_valid(form)


class ItemsListInSongbook(OwnerRequiredMixin, ListView):
    model = ItemsInSongbook
    context_object_name = "items_list"
    template_name = "generator/items_in_songbook.html"
    songbook = None

    def get_queryset(self):
        songbook_id = self.kwargs.get('id', None)
        slug = self.kwargs.get('slug', None)
        self.songbook = get_object_or_404(Songbook, id=songbook_id, slug=slug)
        return ItemsInSongbook.objects.filter(songbook=self.songbook)

    def get_context_data(self, **kwargs):
        context = super(ItemsListInSongbook, self).get_context_data(**kwargs)
        context['songbook'] = self.songbook
        return context


@login_required
def set_current_songbook(request):
    """Set a songbook for edition with sessions
     """
    if (request.GET['songbook'] != None):
        songbook_id = request.GET['songbook']
        request.session['current_songbook'] = int(songbook_id)
        return redirect('song_list')
    else:
        messages.error(request, _(u"Ce carnet n'existe pas."))
        return redirect('songbook_list')


def _add_item(item, songbook, rank, current_item_list):
    """Add an item to a songbook.
    Return True if it has been added, false if not.
    """
    if item not in current_item_list:
        item_in_songbook = ItemsInSongbook(item=item,
                                            songbook=songbook,
                                            rank=rank)
        item_in_songbook.save()
        return True
    else:
        return False


def _get_new_rank(songbook_id):
    """Get the last song in the section, and return this rank plus 1."""
    rank = ItemsInSongbook.objects.filter(songbook=songbook_id).count()
    if rank == None:
        return 1
    else:
        return rank + 1


@login_required
def add_songs_to_songbook(request):
    """Add a list of songs to the current songbook.
    """
    next_url = request.POST['next']

    try:
        songbook_id = request.session['current_songbook']
        songbook = Songbook.objects.get(id=songbook_id)
    except (KeyError, Songbook.DoesNotExist):
        messages.error(request,
                       _(u"Choisissez un carnet pour ajouter ces chants")
                       )
        return redirect(next_url)

    song_list = request.POST.getlist('songs[]')
    current_item_list = songbook.items.all()
    rank = _get_new_rank(songbook_id)

    for song_id in song_list:
        try:
            song = Song.objects.get(id=song_id)
            added = _add_item(item=song,
                              songbook=songbook,
                              rank=rank,
                              current_item_list=current_item_list)
            if added:
                rank += 1
        except Song.DoesNotExist:  # May be useless
            pass

    artist_list = request.POST.getlist('artists[]')
    for artist_id in artist_list:
        try:
            artist = Artist.objects.get(id=artist_id)
            song_list = artist.songs.all()
            for song in song_list:
                added = _add_item(item=song,
                              songbook=songbook,
                              rank=rank,
                              current_item_list=current_item_list)
                if added:
                    rank += 1
        except Artist.DoesNotExist:
            pass

    return redirect(next_url)


@owner_required(('id', 'id'))
def move_or_delete_items(request, id, slug):
    """Remove an item or a list of items from the current songbook
    """
    next_url = request.POST['next']
    songbook = Songbook.objects.get(id=id, slug=slug)
    item_list = {}

    for key in request.POST.keys():
        if key.startswith('item_'):
            item_list[key] = request.POST[key]

    for item_key in item_list.keys():
        item_id = int(item_key[5:])
        try:
            rank = int(item_list[item_key])
            ItemsInSongbook.objects.filter(songbook=songbook,
                                           id=item_id
                                           ).update(rank=rank)
        except ValueError:
            if str(item_list[item_key]).lower() == 'x':
                ItemsInSongbook.objects.filter(
                        songbook=songbook,
                        id=item_id
                        ).delete()

    songbook.fill_holes()

    if request.POST['new_section']:
        try:
            section_name = str(request.POST['new_section'])
            songbook.add_section(section_name)
        except ValueError:
            messages.error(request, _(u"Ce nom de section n'est pas valide"))

    return redirect(next_url)


class DeleteSongbook(OwnerRequiredMixin, DeleteView):
    model = Songbook
    context_object_name = "songbook"
    template_name = 'generator/delete_songbook.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        id = self.kwargs.get('id', None)
        slug = self.kwargs.get('slug', None)
        return get_object_or_404(Songbook, id=id, slug=slug)


@owner_required(('id', 'id'))
def render_songbook(request, id, slug):
    """Trigger the generation of a songbook
    """
    force = request.REQUEST.get("force", False)
    songbook = Songbook.objects.get(id=id)

    # Dummy layout
    from generator.build import _get_layout
    layout = _get_layout()

    try:
        gen_task = GeneratorTask.objects.get(songbook__id=id,
                                             layout__id=layout.id)
        state = gen_task.state
    except GeneratorTask.DoesNotExist:
        gen_task = None
        state = None

    # Build cases
    build = gen_task is None or \
            ((state == GeneratorTask.State.FINISHED or \
              state == GeneratorTask.State.ERROR)  and force) or\
            gen_task.hash != songbook.hash()

    if build:
        gen_task, _created = GeneratorTask.objects.get_or_create(
                                    songbook=songbook,
                                    layout=layout)
        gen_task.result = {}
        gen_task.hash = songbook.hash()
        gen_task.state = GeneratorTask.State.QUEUED
        gen_task.save()

        import generator.tasks as tasks
        tasks.queue_render_task(id, layout.id)

    return redirect(reverse('songbook_private_list') + '#' + id)
