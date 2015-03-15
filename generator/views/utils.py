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

"""Various views"""

from django import template
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.core.mail.message import BadHeaderError
from django.http.response import Http404
from django.shortcuts import render, redirect

from django.views.generic import ListView
import string
from unidecode import unidecode
from collections import OrderedDict


from generator.forms import ContactForm

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


class LetterListView(ListView):
    
    def get_queryset(self):
        queryset = super(LetterListView, self).get_queryset()

        current_letter = self.request.GET.get('letter')
        
        names = queryset.values_list('id', self.name_field)
        self.pages = _construct_pages(names)

        # restrict the queryset according to the selected letter
        try:
            restricted_ids = self.pages[current_letter]
            self.current_letter = current_letter
            queryset = queryset.filter(id__in=restricted_ids)
        except KeyError:
            self.current_letter = False

        return queryset

    def get_context_data(self, **kwargs):
        context = super(LetterListView, self).get_context_data(**kwargs)

        paginator = {'current_letter': self.current_letter}

        # Add the weight of every letter
        paginator['letters'] = _compute_letters_weight(self.pages)

        # Add relative links to previous and next page
        if self.current_letter:
            letters = list(self.pages.keys())

            index = letters.index(self.current_letter)
            if index > 0:
                paginator['previous_letter'] = letters[index - 1]
            if index < len(letters) - 1:
                paginator['next_letter'] = letters[index + 1]

        context['paginator'] = paginator
        return context

def letter_page(name):
    """
    Return the letter associated to the name
    """

    first_letter = unidecode(name[0])
    first_letter = str.upper(first_letter)

    numbers = "0123456789"
    alphabet = string.ascii_uppercase

    if first_letter in alphabet:
        return first_letter
    elif first_letter in numbers:
        return "0-9"
    else:
        return "~"

def _construct_pages(names):
    """
    Construct a dict of all pages 
        key : letter (or "0-9" or "~")
        value : [ids of the objects starting with the key]
    """
    pages = list(string.ascii_uppercase)
    pages.append("0-9")
    pages.append("~")
    pages = OrderedDict([(i,[]) for i in pages])

    for name in names:
        letter = letter_page(name[1])
        pages[letter].append(name[0])

    return pages


def _compute_letters_weight(pages):
    """
    Input : dict of pages with list of ids
        key : letter (or "0-9" or "~")
        value : [ids of the objects starting with the key]

    Output : dict of letters with a weight of the number of ids
        key : letter (or "0-9" or "~")
        value : weight (between 0 and 1) of the number of pages
    """
    # replace the list of ids, with the length
    pages.update((letter, len(ids)) for letter, ids in pages.items())

    sorted_length = sorted(pages.values(), reverse=True)
    num_pages = len(pages)

    def normalize(length):
        if length > 0:
            return str(int(100*sort_normalize(length))/100)
        else:
            return 0
    def sort_normalize(length):
        i = num_pages - sorted_length.index(length)
        return i/num_pages

    pages.update((letter, normalize(length)) for letter, length in pages.items())

    return pages
