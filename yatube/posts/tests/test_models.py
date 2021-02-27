from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="TestUser")
        self.client.force_login(self.user)
        self.post = Post.objects.create(text="Test post", author=self.user)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        posts = self.post
        field_verboses = {
            'text': 'Текст публикации',
            'author': 'Автор публикации',
            'group': 'Группа'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    posts._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым """
        posts = self.post
        field_help_texts = {
            'text': 'Введите текст публикации',
            'group': 'Выберите группу публикации'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    posts._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild(self):
        posts = self.post
        expected_object_name = posts.text
        self.assertEqual(expected_object_name, str(posts))


class GroupModelTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="TestUser")
        self.client.force_login(self.user)
        self.group = Group.objects.create(
            title='leo',
            slug='leo',
            description='leo'
        )

        def test_verbose_name(self):
            """verbose_name в полях совпадает с ожидаемым."""
            group = self.group
            field_verboses = {
                'title': 'Название группы',
                'slug': 'Загаловок группы',
                'description': 'Описание группы',
                'rules': 'Правило группы',
            }
            for value, expected in field_verboses.items():
                with self.subTest(value=value):
                    self.assertEqual(
                        group._meta.get_field(value).verbose_name, expected)

        def test_object_name_is_title_fild(self):
            group = Group.objects.get()
            expected_object_name = group.title
            self.assertEqual(expected_object_name, str(group))
