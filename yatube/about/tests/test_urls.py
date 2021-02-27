from django.test import Client, TestCase

from posts.models import User


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = User.objects.create_user(
            username="TestUser"
        )
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template_auf_user(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_guest_client(self):
        """URL-адрес использует соответствующий шаблон.(Гостевой доступ)"""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
