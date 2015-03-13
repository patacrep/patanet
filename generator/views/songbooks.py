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

"""Songbooks views"""

from django.views.generic import ListView, CreateView, DetailView, UpdateView, \
                                 DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from django.db.models import Count, Prefetch, F


from generator.decorators import LoginRequiredMixin, OwnerOrPublicRequiredMixin, \
                                OwnerRequiredMixin, owner_required, return_json_on_ajax
from generator.models import Songbook, ItemsInSongbook, Song, \
                             Task as GeneratorTask, Layout, Artist
from generator.forms import SongbookCreationForm, LayoutForm


class SongbookPublicList(ListView):
    model = Songbook
    context_object_name = "songbooks"
    template_name = "generator/songbook_public_list.html"

    def get_queryset(self):
        public_songbooks = Songbook.objects.filter(is_public=True
                                   ).order_by('title').prefetch_related(
                                        Prefetch(
                                            'tasks', 
                                            queryset=GeneratorTask.objects.filter(state='FINISHED').select_related('layout'), 
                                            to_attr='finished_tasks')
                                    )

        
        
        # If the user is connected :
        if self.request.user.is_authenticated():
            #  exclude his songbooks from the public list
            public_songbooks = public_songbooks.exclude(user=self.request.user)

            #  fetch his public songbooks (with more related data)
            my_songbooks = SongbookPrivateList.get_queryset(self).exclude(is_public=False)

            # Concatenate the two sets
            from itertools import chain
            public_songbooks = list(chain(public_songbooks, my_songbooks))
        
        _count_and_attach_as_attributes(['song', 'artist', 'section'], public_songbooks)
        return public_songbooks

def _count_item_of_type(item_type, songbooks):
    """
    Count the number of irems of type 'item_type' in all the songbooks with as few queries as possible.
    Return tuple { 'songbook_id' : number_of_items }
    """
    if item_type == "artist":
        return _count_item_of_type_artist(songbooks)

    item_type = ContentType.objects.get(app_label="generator", model=item_type)

    count_items = ItemsInSongbook.objects.filter(
                    songbook__in=songbooks,
                    item_type=item_type,
                    ).values('songbook').annotate(item_quantity=Count("item_id")).order_by('songbook')

    normalized_count = {row['songbook']: row['item_quantity'] for row in count_items}

    return normalized_count

def _count_item_of_type_artist(songbooks):
    """
    Count the number of artists in all the songbooks with as few queries as possible.
    Return tuple { 'songbook_id' : number_of_artists }
    """
    count_artists = Song.objects.filter(
                    items_in_songbook__songbook__in=songbooks,
                    ).values('items_in_songbook__songbook').annotate(artists=Count("artist_id", distinct=True)).order_by('items_in_songbook__songbook')

    normalized_artists = {row['items_in_songbook__songbook']: row['artists'] for row in count_artists}

    return normalized_artists

def _count_and_attach_as_attributes(item_types, songbooks):
    for item_type in item_types:
        count = _count_item_of_type(item_type, songbooks)
        for songbook in songbooks:
            setattr(songbook, item_type + '_quantity', count.get(songbook.id, 0))    

class SongbookPrivateList(LoginRequiredMixin, ListView):
    model = Songbook
    context_object_name = "songbooks"
    template_name = "generator/songbook_private_list.html"

    def get_queryset(self):
        songbooks = Songbook.objects.filter(user=self.request.user
                                       ).order_by('title').prefetch_related(
                                            Prefetch(
                                                'tasks', 
                                                queryset=GeneratorTask.objects.select_related('layout'))
                                        )
        _count_and_attach_as_attributes(['song', 'artist', 'section'], songbooks)
        return songbooks


class NewSongbook(LoginRequiredMixin, CreateView):
    model = Songbook
    template_name = 'generator/new_songbook.html'
    form_class = SongbookCreationForm

    def get_success_url(self):
        return reverse('set_current_songbook') + '?songbook=' + str(self.object.id)

    def form_valid(self, form):
        form.user = self.request.user
        messages.success(self.request, _(u"Le carnet a été créé."))
        return super(NewSongbook, self).form_valid(form)

    def get_initial(self):
        initial = super(NewSongbook, self).get_initial()
        initial["author"] = self.request.user
        return initial


class ShowSongbook(OwnerOrPublicRequiredMixin, DetailView):
    model = Songbook
    template_name = 'generator/show_songbook.html'
    context_object_name = 'songbook'

    def get_queryset(self):
        return Songbook.objects.filter(id=self.kwargs['id'],
                                       slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(ShowSongbook, self).get_context_data(**kwargs)
        base_query = ItemsInSongbook.objects.filter(
                        songbook=self.object
                        ).select_related('item_type')

        # Different queries if it's a song or a section
        song_type = ContentType.objects.get(app_label="generator", model="song")
        song_list = base_query.filter(
                        item_type=song_type
                        ).prefetch_related('item__artist')
        section_type = ContentType.objects.get(app_label="generator", model="section")
        section_list = base_query.filter(
                        item_type=section_type
                        ).prefetch_related('item')

        # Merge the two queries
        items_list = []
        section_index = 0
        section_max = len(section_list)
        song_index = 0
        song_max = len(song_list)
        while section_index < section_max and song_index < song_max:
            item_section = section_list[section_index]
            item_song = song_list[song_index]
            if item_section.rank <= item_song.rank:
                items_list.append(item_section)
                section_index += 1
            else:
                items_list.append(item_song)
                song_index += 1

        # append the remaining elements
        items_list.extend(section_list[section_index:])
        items_list.extend(song_list[song_index:])
        
        context['items_list'] = items_list
        if self.request.user.id == self.object.user_id:
            context['can_edit'] = True
        else:
            context['can_edit'] = False
        return context


class UpdateSongbook(OwnerRequiredMixin, UpdateView):
    model = Songbook
    template_name = 'generator/update_songbook.html'
    form_class = SongbookCreationForm

    def get_queryset(self):
        return Songbook.objects.filter(id=self.kwargs['id'],
                                       slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse('edit_songbook', kwargs=self.kwargs)


    def form_valid(self, form):
        form.user = self.request.user
        messages.success(self.request, _(u"Le carnet a été modifié."))
        # Update songbook slug
        self.kwargs["slug"] = slugify(form.cleaned_data["title"])
        return super(UpdateSongbook, self).form_valid(form)


@login_required
def set_current_songbook(request):
    """Set a songbook for edition with sessions
     """
    next = request.GET.get('next', 'artist_list')
    try:
        _set_and_get_current_songbook(request, request.GET.get('songbook'))
    except (KeyError, Songbook.DoesNotExist):
        messages.error(request, _(u"Ce carnet n'existe pas."))
        next = 'songbook_private_list'
    return redirect(next)

def _set_and_get_current_songbook(request, songbook_id):
    songbook = Songbook.objects.get(id=songbook_id, user_id=request.user.id)
    if request.session.get('current_songbook') != songbook_id:
        request.session['current_songbook'] = songbook_id
    return songbook

@login_required
@return_json_on_ajax
def add_songs_to_songbook(request):
    """Add a list of songs to the current songbook.
    """
    next_url = request.POST.get('next', 'artist_list')

    try:
        songbook = _set_and_get_current_songbook(request, request.POST.get('current_songbook'))
    except (KeyError, Songbook.DoesNotExist):
        messages.error(request,
                       _(u"Ce carnet n'existe plus.")
                       )
        return redirect(next_url)

    song_id_list = request.POST.getlist('songs[]')
    song_list = Song.objects.filter(
                        id__in=song_id_list,
                        ).exclude(
                        items_in_songbook__songbook=songbook
                        )

    item_count = ItemsInSongbook.objects.filter(songbook=songbook).count()
    items_to_insert = []
    for song in song_list:
        item_count += 1
        items_to_insert.append(
                                ItemsInSongbook(item=song,
                                            songbook=songbook,
                                            rank=item_count)
                              )

    ItemsInSongbook.objects.bulk_create(items_to_insert)
    songbook.fill_holes()

    song_added = len(items_to_insert)
    if song_added == 0:
        messages.info(request, _(u"Aucun chant ajouté"))
    elif song_added == 1:
        messages.success(request, _(u"Chant ajouté au carnet"))
    else:
        messages.success(request, _(u"%i chants ajoutés au carnet" % (song_added) ))

    return redirect(next_url)

@login_required
@return_json_on_ajax
def remove_songs(request):
    """Remove a song from the current songbook"""
    next_url = request.POST.get('next', 'artist_list')

    try:
        songbook = _set_and_get_current_songbook(request, request.POST.get('current_songbook'))
    except (KeyError, Songbook.DoesNotExist):
        messages.error(request,
                       _(u"Ce carnet n'existe plus.")
                       )
        return redirect(next_url)
    song_ids = request.POST.getlist('songs[]')
    type = ContentType.objects.get(app_label="generator", model="song")
    try:
        items = ItemsInSongbook.objects.filter(songbook=songbook,
                                           item_type=type,
                                           item_id__in=song_ids)
    except (KeyError, ItemsInSongbook.DoesNotExist):
        messages.info(request,
                       _(u"Ce chant n'appartient pas au carnet")
                       )
        return redirect(next_url)

    # Update the rank of the items that are between the deleted items
    ranks = items.values_list('rank', flat=True)
    previous_rank = None
    for idx, current_rank in enumerate(ranks):
        if previous_rank and (current_rank - previous_rank) > 1:
            ItemsInSongbook.objects.filter(songbook=songbook,
                                           rank__gt=previous_rank,
                                           rank__lt=current_rank,
                                           ).update(rank=F('rank')-idx)
        previous_rank = current_rank

    # Update the rank of the items that are after the last deleted item
    if previous_rank:
        ItemsInSongbook.objects.filter(songbook=songbook,
                                       rank__gt=previous_rank,
                                       ).update(rank=F('rank')-idx-1)

    song_removed = len(items)
    items.delete()
    songbook.fill_holes()

    if song_removed == 0:
        messages.info(request, _(u"Aucun chant retiré"))
    elif song_removed == 1:
        messages.success(request, _(u"Chant retiré du carnet"), extra_tags='removal')
    else:
        messages.success(request, _(u"%i chants retirés du carnet" % (song_removed) ), extra_tags='removal')
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
            messages.success(request, _(u"Nouvelle section ajoutée en fin de carnet"))
        except ValueError:
            messages.error(request, _(u"Ce nom de section n'est pas valide"))

    section_list = {}
    for key in request.POST.keys():
        if key.startswith('section_'):
            section_list[key] = request.POST[key]

    for key, section_name in section_list.items():
        item_id = int(key[8:])
        section = ItemsInSongbook.objects.get(songbook=songbook,
                                              id=item_id)

        if section.item.name != section_name:
            error, message = _clean_latex(section_name)
            if error:
                messages.error(request, message)
            else:
                section.item.name = section_name
                section.item.save()

    return redirect(next_url)

def _clean_latex(string):
        '''
        Return true if one of the LaTeX special characters
        is in the string
        '''
        TEX_CHAR = ['\\', '{', '}', '&', '[', ']', '^', '~']
        CHARS = ', '.join(['"{char}"'.format(char=char) for char in TEX_CHAR])
        MESSAGE = _(u"Les caractères suivant sont interdits, merci de les " +
                    u"supprimer : {chars}.".format(chars=CHARS))
        for char in TEX_CHAR:
            if char in string:
                return True, MESSAGE
        return False, ""


class DeleteSongbook(OwnerRequiredMixin, DeleteView):
    model = Songbook
    context_object_name = "songbook"
    template_name = 'generator/delete_songbook.html'

    def get_success_url(self):
        success_url = reverse_lazy('songbook_private_list')
        messages.success(self.request, _(u"Le carnet a été supprimé"), extra_tags='removal')
        return success_url

    def get_object(self, queryset=None):
        id = self.kwargs.get('id', None)
        slug = self.kwargs.get('slug', None)
        return get_object_or_404(Songbook, id=id, slug=slug)


class LayoutList(OwnerRequiredMixin, CreateView):
    """Setup the parameters for songbook rendering
    """
    model = Layout
    template_name = 'generator/setup_rendering.html'
    form_class = LayoutForm

    def get_success_url(self):
        return reverse('render_songbook',
                        kwargs={"id": self.kwargs["id"],
                                "slug": self.kwargs["slug"]})

    def form_valid(self, form):
        messages.success(self.request, _(u"La mise en page a été crée."))
        rst = super(LayoutList, self).form_valid(form)

        # Set the session for layout generation
        self.request.session["layout"] = self.object.id
        return rst

    def get_context_data(self, **kwargs):
        context = super(LayoutList, self).get_context_data(**kwargs)
        id = self.kwargs.get('id', None)
        slug = self.kwargs.get('slug', None)
        songbook = Songbook.objects.get(id=id, slug=slug)
        context['songbook'] = songbook
        context['form_options'] = LayoutForm.OPTIONS
        context['existing_tasks'] = GeneratorTask.objects.filter(
                                                    songbook=songbook)
        return context


@owner_required(('id', 'id'))
def render_songbook(request, id, slug):
    """Trigger the generation of a songbook
    """
    force = request.REQUEST.get("force", False)
    songbook = Songbook.objects.get(id=id)

    layout_id = request.REQUEST.get("layout", 0)

    if layout_id == 0:
        layout_id = request.session["layout"]

    layout = Layout.objects.get(id=layout_id)

    try:
        gen_task = GeneratorTask.objects.get(songbook=songbook,
                                             layout=layout)
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
        tasks.queue_render_task(gen_task.id)

    return redirect(reverse('setup_rendering', kwargs={"id":id, "slug":slug}))
