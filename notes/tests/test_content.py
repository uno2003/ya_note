from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone

from notes.models import Note

User = get_user_model()

class TestHomePage(TestCase):
    HOME_URL = reverse('notes:home')
    @classmethod
    def setUpTestData(cls):
        today = datetime.today()

    def test_home_view(self):
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/home.html')
