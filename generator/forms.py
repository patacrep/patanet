# # -*- coding: utf-8 -*-
# Copyright (c) 2014 The songbook Team
#
# This program is distributed under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2 of the License, or any later version.
# For more information, see the file LICENCE.txt


from django import forms
from generator.models import Profile, Song, Songbook
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.core.mail import mail_admins, send_mail
from django.utils.html import escape
from django.conf import settings
from django.contrib.sites.models import Site


class RegisterForm(UserCreationForm):
    """ Require email address when a user signs up """
    email = forms.EmailField(label='Email address',
                             max_length=255,
                             required=True)

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = _("Adresse mail")
        self.fields['username'].help_text = _("30 caractères maximum.")
        self.fields['password2'].help_text = None

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
            raise forms.ValidationError(_("Cette adresse mail existe déjà. "
                                "Si vous avez oublié votre mot de passe, "
                                "vous pouvez le réinitialiser."))
        except User.DoesNotExist:
            return email

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


ADMIN_MESSAGE = _(
'''{user_info} vous a envoyé un message depuis le site {sitename}.

================================================================
{message}
================================================================

Merci de répondre directement à son adresse mail : {sender_mail}'''
)

USER_MESSAGE = _(
'''Vous avez envoyé un message depuis le site {sitename}. Voici
la copie reçue par les administrateurs.

================================================================
{message}
================================================================

Merci d'utiliser ce site, cordialement,
Les Administrateurs.

PS : Ce message est envoyé automatiquement. Merci de ne pas y répondre,
Les administrateurs prendont contact avec vous.'''
)


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100,
                              label=_("Sujet"))
    sender = forms.EmailField(label=_("Votre adresse mail"))
    message = forms.CharField(widget=forms.Textarea,
                              label=_("Votre message"))
    send_copy = forms.BooleanField(
                label=_("Recevoir une copie du mail"),
                required=False)

    def send_mail(self, username):
        '''Send the contact email. Data should have been cleaned before.
        '''
        message = self._make_admin_message(username)
        subject = self.cleaned_data['subject']
        mail_admins(subject, message, fail_silently=False)

        if self.cleaned_data['send_copy']:
            message = self._make_user_message()
            send_mail(subject,
                      message,
                      settings.DEFAULT_FROM_EMAIL,
                      [self.cleaned_data['sender']])

    def _make_admin_message(self, username):
        '''Adds some information in the message send to the admins
        '''
        if username is not None:
            user_info = username + " (" + self.cleaned_data['sender'] + ") "
        else:
            user_info = self.cleaned_data['sender']

        message = ADMIN_MESSAGE.format(user_info=user_info,
                 sitename=Site.objects.get_current().name,
                 message=escape(self.cleaned_data['message']),
                 sender_mail=self.cleaned_data['sender'])

        return message

    def _make_user_message(self):
        '''Adds some information in the message send to the user
        '''
        message = USER_MESSAGE.format(sitename=Site.objects.get_current().name,
                 message=escape(self.cleaned_data['message']),
                 )

        return message


class SongbookCreationForm(forms.ModelForm):
    class Meta:
        model = Songbook
        fields = ('title', 'description', 'is_public')

    def save(self, force_insert=False, force_update=False, commit=True):
        new_songbook = super(SongbookCreationForm, self).save(commit=False)
        # User is gotten in the view
        user_profile = Profile.objects.get(user=self.user)
        new_songbook.user = user_profile
        new_songbook.slug = slugify(new_songbook.title)

        if commit:
            new_songbook.save()
        return new_songbook


class SongbookLayoutForm(forms.ModelForm):
    BOOK_OPTIONS = [('diagram', _("Diagrammes d'accords")),
            ('importantdiagramonly', _("Diagrammes important seulement")),
            ('repeatchords', _("Accords sur tous les couplets")),
            ('tabs', _("Tablatures")),
            ('lilypond', _('Partitions Lilypond')),
            ('pictures', _("Couvertures d'albums")),
            ('onesongperpage', _("Une chanson par page")),
            ]
    CHORDED = 'chorded'
    LYRICS = 'lyrics'
    BOOK_TYPES = (
        (CHORDED, _('Avec accords')),
        (LYRICS, _('Sans accords')),
        )

    template = forms.CharField(initial='patacrep.tmpl',
                             label=_("Mise en forme avec le gabarit")
                             )
    bookoptions = forms.MultipleChoiceField(
                            choices=BOOK_OPTIONS,
                            label=_('Options du receuil'),
                            widget=forms.CheckboxSelectMultiple(),
                            required=False
                            )

    class Meta:
        pass
        # model = Layout
        # fields = ('title', 'description', 'is_public', 'booktype')
        # template
