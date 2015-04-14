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
from django.db.models import Count, Prefetch, F, Q
from django.core.exceptions import ValidationError


from generator.decorators import LoginRequiredMixin, OwnerOrPublicRequiredMixin, \
                                OwnerRequiredMixin, owner_required, return_json_on_ajax
from generator.models import Songbook, ItemsInSongbook, Song, \
                             Task as GeneratorTask, Layout, Artist, Section
from generator.forms import SongbookCreationForm, LayoutForm, validate_latex_free


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
        context['form_options'] = LayoutForm.OPTIONS
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


    """
    Parse the POST data into some arrays
    """
    posted_section_name = {}
    remove_array = []
    posted_rank_list = {}
    for key, value in request.POST.items():

        if key.startswith('section_'):
            key = int(key[8:])
            posted_section_name[key] = value
        elif key.startswith('item_'):
            key = int(key[5:])
            if str(value).lower() == 'x':
                remove_array.append(key)
            else:
                posted_rank_list[key] = int(value)


    """
    Remove the items from the songbook
    """
    # The sections will be removed with a dedicated query
    remove_section_array = []
    for key in remove_array:
        if key in posted_section_name:
            remove_section_array.append(key)
            # Remove this section from the other arrays (renaming and generic item removal)
            del posted_section_name[key]
            remove_array.remove(key)

    # Remove the Sections from the songbook
    Section.objects.filter(
            items_in_songbook__songbook=songbook,
            items_in_songbook__id__in=remove_section_array
            ).delete()

    # Remove the items from the songbook
    ItemsInSongbook.objects.filter(
            songbook=songbook,
            id__in=remove_array
            ).delete()
    
    """
    Add the new section(s) to the songbook
    """
    # Section added without javascript
    if request.POST['new_section']:
        try:
            section_name = str(request.POST['new_section'])
            songbook.add_section(section_name)
            messages.success(request, _(u"Nouvelle section ajoutée en fin de carnet"))
        except ValidationError as e:
            messages.error(request, e.message_dict['name'][0])

    # Sections added with javascript
    new_sections = request.POST.getlist('new_section[]')
    if new_sections:
        new_ranks = request.POST.getlist('new_item[]')
        for index, section_name in enumerate(new_sections):
            if not section_name:
                continue
            try:
                new_rank = int(new_ranks[index])
            except ValueError: # because the rank is now 'X'
                continue
            try:
                songbook.add_section(section_name, new_rank)
            except ValidationError as e:
                messages.error(request, e.message_dict['name'][0])


    """
    Rename the section that need to be renamed
    """
    section_list = Section.objects.filter(
                    items_in_songbook__songbook=songbook,
                    ).values('id', 'name', 'items_in_songbook__id')

    for section in section_list:
        item_id = section['items_in_songbook__id']
        new_name = posted_section_name.get(item_id)
        if new_name and section['name'] != new_name:
            try:
                # We need to validate manually
                validate_latex_free(new_name)
                Section.objects.filter(id=section['id']).update(name=new_name)
            except ValidationError as e:
                messages.error(request, e.messages[0])

    """
    Set an increasing the rank for all items
    """
    # list all the rank of the current elements, and set the new rank
    old_rank_list = ItemsInSongbook.objects.filter(songbook=songbook).values_list('id','rank')
    new_rank_list = []
    for item_id, old_rank in old_rank_list:
        new_rank = old_rank
        if posted_rank_list.get(item_id, 0) > 0:
            new_rank = posted_rank_list[item_id]
        new_rank_list.append((item_id, new_rank))

    # Sort the list according to the new rank
    new_rank_list = sorted(new_rank_list, key=lambda x: x[1])

    # update the rank of each item in the DB if necessary
    old_rank_dict = dict(old_rank_list)
    rank = 1
    for key in new_rank_list:
        item_id = key[0]
        if rank != old_rank_dict[item_id]:
            ItemsInSongbook.objects.filter(songbook=songbook,
                                           id=item_id
                                           ).update(rank=rank)
        rank += 1

    return redirect(next_url)

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


class NewLayout(OwnerRequiredMixin, CreateView):
    """Create new parameters for songbook rendering
    """
    model = Layout
    template_name = 'generator/new_download.html'
    form_class = LayoutForm

    def get_success_url(self):
        return reverse('download_songbook',
                        kwargs={"id": self.kwargs["id"],
                                "slug": self.kwargs["slug"]})

    def form_valid(self, form):
        form.user = self.request.user
        messages.success(self.request, _(u"La mise en page a été créée."))
        return super(NewLayout, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(NewLayout, self).get_context_data(**kwargs)
        id = self.kwargs.get('id', None)
        slug = self.kwargs.get('slug', None)
        songbook = get_object_or_404(Songbook, id=id, slug=slug)
        context['songbook'] = songbook
        return context


class LayoutList(OwnerRequiredMixin, ListView):
    """Setup the parameters for songbook rendering
    """
    model = Layout
    context_object_name = "layouts"
    template_name = 'generator/download_songbook.html'

    def get_queryset(self):
        return Layout.objects.filter(
                    Q(user_id=self.request.user.id)
                    | Q(user_id=None)
                )

    def get_context_data(self, **kwargs):
        context = super(LayoutList, self).get_context_data(**kwargs)

        id = self.kwargs.get('id', None)
        slug = self.kwargs.get('slug', None)
        songbook = Songbook.objects.get(id=id, slug=slug)
        context['songbook'] = songbook
        context['songbook_hash'] = songbook.hash()

        context['form_options'] = LayoutForm.OPTIONS
        context['can_edit'] = True
        return context


def get_task_link(request, id):
    task = get_object_or_404(GeneratorTask, id=id)
    songbook = task.songbook
    if not songbook.is_public and request.user.id != songbook.user_id:
        return redirect(reverse('denied'))
    context = {
        'task': task,
        'songbook': songbook,
        'songbook_hash' : songbook.hash()
    }
    return render(request, 'generator/layout/download_links.html', context)


@owner_required(('id', 'id'))
def render_songbook(request, id, slug):
    """Trigger the generation of a songbook
    """
    force = request.REQUEST.get("force", False)
    songbook = Songbook.objects.get(id=id)

    layout_id = request.REQUEST.get("layout", 0)

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
    elif state == GeneratorTask.State.ERROR:
        messages.error(request, _(u"Le bug doit être corrigé pour relancer la compilation: merci de contacter un administrateur"))

    return redirect(reverse('download_songbook', kwargs={"id":id, "slug":slug}))
