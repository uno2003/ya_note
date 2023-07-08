import unittest
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

# Импортируем из файла с формами список стоп-слов и предупреждение формы.
# Загляните в news/forms.py, разберитесь с их назначением.
from notes.models import Note

User = get_user_model()


class TestNoeCreations(TestCase):
    NOTE_TEXT = "Эльфы - вечные"
    NOTE_TITLE = "Властелин колец"
    NOTE_SLUG = "frodo"

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Бильбо Бэггинс')
        # cls.note = Note.objects.create(title='Заголовок', text='Текст', slug='text', author=cls.user)
        cls.url = reverse('notes:detail', args=(cls.NOTE_SLUG,))
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'text': cls.NOTE_TEXT, 'slug': cls.NOTE_SLUG, 'title': cls.NOTE_TITLE}

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        name = ('notes:add')
        name_done= ('notes:success')
        response = self.auth_client.post(reverse(name, None), data=self.form_data)
        self.assertRedirects(response, reverse(name_done, None))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.author, self.user)

class TestNoteEditDelete(TestCase):
    # Тексты для комментариев не нужно дополнительно создавать
    # (в отличие от объектов в БД), им не нужны ссылки на self или cls,
    # поэтому их можно перечислить просто в атрибутах класса.
    NOTE_TEXT = "Эльфы - вечные"
    NEW_NOTE_TEXT = "Гномы - мелкие"
    NOTE_TITLE = "Властелин колец"
    NOTE_SLUG = "frodo"

    @classmethod
    def setUpTestData(cls):
        # Создаём новость в БД.
        cls.author = User.objects.create(username='Гендальф')
        cls.note = Note.objects.create(title=cls.NOTE_TITLE, text=cls.NOTE_TEXT, slug=cls.NOTE_SLUG, author=cls.author)
        # Формируем адрес блока с комментариями, который понадобится для тестов.
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))  # Адрес новости.
        # Создаём пользователя - автора комментария.

        # Создаём клиент для пользователя-автора.
        cls.author_client = Client()
        # "Логиним" пользователя в клиенте.
        cls.author_client.force_login(cls.author)
        # Делаем всё то же самое для пользователя-читателя.
        cls.reader = User.objects.create(username='Саруман')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Создаём объект комментария.

        # URL для редактирования комментария.
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        # URL для удаления комментария.
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        # Формируем данные для POST-запроса по обновлению комментария.
        cls.form_data = {'text': cls.NEW_NOTE_TEXT}
    #
    def test_author_can_delete_note(self):
        # От имени автора комментария отправляем DELETE-запрос на удаление.
        response = self.author_client.delete(self.delete_url)
        # Проверяем, что редирект привёл к разделу с комментариями.
        # Заодно проверим статус-коды ответов.
        self.assertRedirects(response, self.note_url)
        # Считаем количество комментариев в системе.
        notes_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(notes_count, 0)
    #
    def test_user_cant_delete_note_of_another_user(self):
        # Выполняем запрос на удаление от пользователя-читателя.
        response = self.reader_client.delete(self.delete_url)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что комментарий по-прежнему на месте.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
    #
    def test_author_can_edit_note(self):
        # Выполняем запрос на редактирование от имени автора комментария.
        response = self.author_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, self.note_url)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст комментария соответствует обновленному.
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
    #
    def test_user_cant_edit_note_of_another_user(self):
        # Выполняем запрос на редактирование от имени другого пользователя.
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст остался тем же, что и был.
        self.assertEqual(self.note.text, self.NOTE_TEXT)