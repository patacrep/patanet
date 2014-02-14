from django.test import TransactionTestCase
from django.test.utils import override_settings
from generator.models import *


class AddRemove(TransactionTestCase):

    fixtures = ["test_data_1.json"]

    def setUp(self):        
        pass

    def test_add_song_to_songbook(self):
        
        # pre-conditions
        
        self.assertGreater(Songbook.objects.count(), 0)
        self.assertGreater(Song.objects.count(), 0)

        song = Song.objects.all()[0]
        songbook = Songbook.objects.get(id=1)

        self.assertEqual(songbook.items.count(), 0)

        # operations
        
        songbook.add(song)
        
        # verification
        
        sis = SongInSongbook.objects.get(song_id=song.id)
        self.assertIsNotNone(sis)
        
        self.assertEqual(sis.title, song.title)
        self.assertEqual(sis.slug, song.slug)
        self.assertEqual(sis.language, song.language)
        self.assertEqual(sis.capo, song.capo)
        
        ais = sis.artist
        self.assertIsNotNone(ais)
        
        self.assertEqual(ais.name, song.artist.name)
        self.assertEqual(ais.slug, song.artist.slug)
        
        fis = sis.file
        self.assertIsNotNone(fis)
        
        self.assertEqual(fis.file_path, song.file.file_path)
        self.assertEqual(fis.object_hash, song.file.object_hash)
        self.assertEqual(fis.commit_hash, song.file.commit_hash)
                
    @override_settings(DEBUG=True)
    def test_remove_song_from_songbook(self):
        
        # pre-conditions

        song = Song.objects.all()[0]
        songbook = Songbook.objects.get(id=1)

        self.assertEqual(ItemsInSongbook.objects.count(), 0)
        self.assertEqual(ArtistInSongbook.objects.count(), 0)
        self.assertEqual(FileInSongbook.objects.count(), 0)
        self.assertEqual(SongInSongbook.objects.count(), 0)

        songbook.add(song)

        self.assertEqual(SongInSongbook.objects.count(), 1)
        self.assertEqual(ArtistInSongbook.objects.count(), 1)
        self.assertEqual(FileInSongbook.objects.count(), 1)
        self.assertEqual(ItemsInSongbook.objects.count(), 1)
        
        # operation
        
        songbook.remove_song(song.id)
        
        self.assertEqual(SongInSongbook.objects.count(), 0)
        self.assertEqual(ItemsInSongbook.objects.count(), 0)
        self.assertEqual(ArtistInSongbook.objects.count(), 0)
        self.assertEqual(FileInSongbook.objects.count(), 0)
        
    @override_settings(DEBUG=True)
    def test_add_twice_remove_once(self):
        
        # pre-conditions
        
        song = Song.objects.all()[0]
        songbook1 = Songbook.objects.get(id=1)
        songbook2 = Songbook.objects.get(id=2)

        self.assertIsNotNone(song)
        self.assertIsNotNone(songbook1)
        self.assertIsNotNone(songbook2)
        
        self.assertEqual(ItemsInSongbook.objects.count(), 0)
        self.assertEqual(ArtistInSongbook.objects.count(), 0)
        self.assertEqual(FileInSongbook.objects.count(), 0)
        self.assertEqual(SongInSongbook.objects.count(), 0)
        
        # action
        
        songbook1.add_song(song)
        songbook2.add_song(song)
        
        self.assertEqual(ItemsInSongbook.objects.count(), 2)
        # There should be only one Song- / ArtistInSongbook instances, as
        # the same song was added twice
        self.assertEqual(FileInSongbook.objects.count(), 1)
        self.assertEqual(SongInSongbook.objects.count(), 1)
        self.assertEqual(ArtistInSongbook.objects.count(), 1)

        songbook2.remove_song(song.id)
        
        # There should still be one *InSongbook instance
        self.assertEqual(ArtistInSongbook.objects.count(), 1)
        self.assertEqual(FileInSongbook.objects.count(), 1)
        self.assertEqual(ItemsInSongbook.objects.count(), 1)
        self.assertEqual(SongInSongbook.objects.count(), 1)

        songbook1.remove_song(song.id)
        
        self.assertEqual(ItemsInSongbook.objects.count(), 0)
        self.assertEqual(ArtistInSongbook.objects.count(), 0)
        self.assertEqual(FileInSongbook.objects.count(), 0)
        self.assertEqual(SongInSongbook.objects.count(), 0)


class Versions(TransactionTestCase):
    
    fixtures = ["test_data_1.json"]

    def setUp(self):        
        pass

    def test_add_2_versions_of_a_song_in_different_songbooks(self):

        # pre-requisites
        song = Song.objects.all()[0]
        songbook1 = Songbook.objects.get(id=1)
        songbook2 = Songbook.objects.get(id=2)

        self.assertIsNotNone(song)
        self.assertIsNotNone(songbook1)
        self.assertIsNotNone(songbook2)
        
        self.assertEqual(ItemsInSongbook.objects.count(), 0)
        self.assertEqual(ArtistInSongbook.objects.count(), 0)
        self.assertEqual(FileInSongbook.objects.count(), 0)
        self.assertEqual(SongInSongbook.objects.count(), 0)

        song_title_old = song.title
        song_slug_old = song.slug
        song_object_hash_old = song.file.object_hash
        song_commit_hash_old = song.file.commit_hash
        
        songbook1.add_song(song)
        
        # build a new version of the song
        song.title = "New title"
        song.slug = "new-slug"
        
        song.file.object_hash = "1234"
        song.file.commit_hash = "5678"

        song.file.save()
        song.save()
        
        songbook2.add_song(song)
        
        self.assertEqual(ItemsInSongbook.objects.count(), 2)
        self.assertEqual(SongInSongbook.objects.count(), 2)
        self.assertEqual(FileInSongbook.objects.count(), 2)
        self.assertEqual(ArtistInSongbook.objects.count(), 1)
        
        sis1 = songbook1.get_songinsongbook_for_song(song.id)
        
        self.assertIsNotNone(sis1)
        self.assertEqual(sis1.title, song_title_old)
        self.assertEqual(sis1.slug, song_slug_old)
        self.assertEqual(sis1.file.object_hash, song_object_hash_old)
        self.assertEqual(sis1.file.commit_hash, song_commit_hash_old)
        
        sis2 = songbook2.get_songinsongbook_for_song(song.id)
        
        self.assertIsNotNone(sis2)
        self.assertEqual(sis2.title, song.title)
        self.assertEqual(sis2.slug, song.slug)
        self.assertEqual(sis2.file.object_hash, song.file.object_hash)
        self.assertEqual(sis2.file.commit_hash, song.file.commit_hash)
        