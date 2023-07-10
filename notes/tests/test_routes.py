# news/tests/test_routes.py
from http import HTTPStatus

from django.contrib.auth import get_user_model

from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

class TestRoutes(TestCase):
    LIST_URLS = ['notes:edit', 'notes:delete', 'notes:detail']
    @classmethod
    def setUpTestData(cls):
        cls.list_url = reverse('notes:list')
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            author=cls.author,
            text='Текст заметки',
            slug='test'
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_availability_for_notes_detail_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in self.LIST_URLS:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_for_list_notes_author(self):
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous(self):
        login_url = reverse('users:login')
        for name in self.LIST_URLS:
            with self.subTest(name=name):
                url=reverse(name, args=(self.note.slug, ))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_redirect_for_anonymous_add_list(self):
        urls = (
            ('notes:add', None),
            ('notes:list', None)
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url=reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)