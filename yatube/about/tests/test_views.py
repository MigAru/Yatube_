from django.test import Client, TestCase

from posts.models import User


class AboutPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template_auth(self):
        templates_pages_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response_auth = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response_auth, template)

    def test_pages_uses_correct_template_guest(self):
        templates_pages_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response_guest = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response_guest, template)
