from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = User.objects.create_user(username="TestUser")
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            id=1,
            title='leo',
            slug='leo',
            description='leo'
        )
        self.post = Post.objects.create(
            text="Test post",
            author=self.user,
            group=self.group
        )
        self.authorized_client_second = Client()
        self.user_second = User.objects.create_user(username="TestUser_second")
        self.authorized_client_second.force_login(self.user_second)

    def test_url_none_auth(self):
        """Проверка URL на доступность гостю и redinect"""
        templates_url = {
            '/': 200,
            '/about/tech/': 200,
            '/about/author/': 200,
            '/new/': 302,
            f'/{self.user.username}/': 200,
            f'/group/{self.group.slug}/': 200,
            f'/{self.user.username}/{self.post.pk}/': 200,
            f'/{self.user.username}/{self.post.pk}/edit/': 302,
            '/unusable/' : 404

        }
        for reverse_name, code_status in templates_url.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, code_status)
        response_2 = self.authorized_client_second.get(
            reverse(
                'post_edit',
                kwargs={'username': self.user, "post_id": self.post.pk}
            )
        )
        self.assertEqual(response_2.status_code, 302)
        self.assertRedirects(
            response_2,
            reverse(
                'post',
                kwargs={'username': self.user, "post_id": self.post.pk}
            )
        )

    def test_url_auth(self):
        """Проверка URL на доступность авторизованному пользователю"""
        templates_url = {
            '/': 200,
            '/about/tech/': 200,
            '/about/author/': 200,
            '/new/': 200,
            f'/{self.user.username}/': 200,
            f'/group/{self.group.slug}/': 200,
            f'/{self.user.username}/{self.post.pk}/': 200,
            f'/{self.user.username}/{self.post.pk}/edit/': 200,
            '/unusable/' : 404
        }
        for reverse_name, code_status in templates_url.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, code_status)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            '/group/leo/': 'group.html',
            '/new/': 'form.html',
            f'/{self.user.username}/{self.post.pk}/': 'post.html',
            f'/{self.user.username}/{self.post.pk}/edit/': 'form.html'
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
