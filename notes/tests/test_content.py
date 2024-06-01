from django.urls import reverse

from notes.forms import NoteForm
from notes.tests.conftest import BaseTest


class TestContent(BaseTest):

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
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            url = reverse(name, args=args)
            with self.subTest(name=name):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
