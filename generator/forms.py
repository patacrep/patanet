# # -*- coding: utf-8 -*-
from django import forms
from generator.models import Profile, Song, Songbook
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


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


class SongbookOptionsForm(forms.ModelForm):
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
        model = Songbook
        fields = ('title', 'description', 'is_public', 'booktype')  # template

    def save(self, force_insert=False, force_update=False, commit=True):
        new_songbook = super(SongbookOptionsForm, self).save(commit=False)
        # User is gotten in the view
        user_profile = Profile.objects.get(user=self.user)
        new_songbook.user = user_profile
        new_songbook.slug = slugify(new_songbook.title)
        new_songbook.bookoptions = self.cleaned_data['bookoptions']

        if commit:
            new_songbook.save()
        return new_songbook


class SongForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Song
        fields = ('title',
                  'artist',
                  'language',
                  'capo',
                  'content',
                  )

    def save(self, force_insert=False, force_update=False, commit=True):
        new_song = super(SongForm, self).save(commit=False)
        new_song.slug = slugify(new_song.title)
        # Create the content of the file and the filename :
        # SONGS_LIBRARY_DIR/<artist>/<title>.sg
        file_content = self.make_sg_content()
        # Create the file instance for content_file
        new_song.content_file = self.make_sg_file(file_content,
                                                  new_song.slug)
        if commit:
            new_song.save()
        return new_song

    def make_sg_content(self):
        # TODO: Ajouter les commandes \capo, \beginsong, etc. au champ content
        pass

    def make_sg_file(self, file_content, slug):
        # TODO: return a file instance
        # filename = slug + '.sg'
        pass
