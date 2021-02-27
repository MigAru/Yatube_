import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostFormTestsWithGroup(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.user = User.objects.create_user(username="TestUser")
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='TestGroup',
            slug='Test',
            description='It is test group'
        )
        self.post = Post.objects.create(
            text="Test post",
            author=self.user,
            group=self.group
        )
        self.post_count = Post.objects.count()

    def test_cant_create_existing_slug(self):
        post_count = self.post_count
        form_data = {
            'group': self.group,
            'text': self.post.text,
        }
        response = self.authorized_client.post(
            reverse('index'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, 200)

    def test_new_post(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post_count = self.post_count
        text = 'Проверка нового поста!'
        form_data = {
            'text': text,
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data
        )

        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(response.status_code, 302)

    def test_edit_post(self):
        post_count = self.post_count
        text = 'Проверка изменения текста!'
        form_data = {
            'text': text,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user,
                    'post_id': self.post.pk
                }
            ),
            data=form_data
        )
        response_index = self.authorized_client.post(
            reverse('index')
        )
        post = response_index.context.get('page')[0]
        self.assertEqual(post.text, text)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, 302)
