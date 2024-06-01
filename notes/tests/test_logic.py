from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note
from notes.tests.conftest import BaseTestLogicWithNote, BaseTestLogic

from pytils.translit import slugify  # type: ignore

User = get_user_model()


class TestLogicCreate(BaseTestLogic):

    def test_user_can_create_note(self):
        """Тест, что залогиненный пользователь может создать заметку."""
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Тест, что анонимный пользователь не может создать заметку."""
        response = self.client.post(self.add_url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_empty_slug(self):
        """
        Тест, что при пустом поле slug
        это поле будет сформировано автоматически
        """
        self.form_data.pop('slug')
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestLogicCreateDelete(BaseTestLogicWithNote):

    def test_not_unique_slug(self):
        """Тест, что нельзя создать 2 заметки с одинаковым slug."""
        self.form_data['slug'] = self.note.slug
        response = self.auth_client.post(
            reverse('notes:add'), data=self.form_data
        )
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Тест, что автор заметки может ее редактировать."""
        response = self.auth_client.post(self.edit_url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """
        Тест, что другой пользователь
        не может редактировать чужую заметку.
        """
        response = self.not_auth_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Тест, что автор может удалить свою заметку."""
        response = self.auth_client.post(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_other_user_cant_delete_note(self):
        """Тест, что друго пользователь не может удалить чужую заметку."""
        response = self.not_auth_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
