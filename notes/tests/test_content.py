from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='slug',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        """
        Тест проверки, что отдельная заметка
        передаётся на страницу со списком заметок.
        Для разных полбзователей.
        """
        users_truth = (
            (self.author, True),
            (self.not_author, False),
        )
        for user, truth in users_truth:
            self.client.force_login(user)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertTrue((self.note in object_list) is truth)

    def test_pages_contains_form(self):
        """
        Тест передачи объекта формы на
        страницы создания и редактирования заметки.
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', self.note),
        )
        self.client.force_login(self.author)
        for name, note_object in urls:
            if note_object is not None:
                url = reverse(name, args=(note_object.slug,))
            else:
                url = reverse(name)
            with self.subTest(name=name):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
