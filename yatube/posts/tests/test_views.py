import shutil 
import tempfile 
 
from django import forms 
from django.conf import settings 
from django.core.cache import cache 
from django.core.files.uploadedfile import SimpleUploadedFile 
from django.test import Client, TestCase 
from django.urls import reverse 
 
from posts.models import Follow, Group, Post, User 
 
 
class PostPagesTests(TestCase): 
    @classmethod 
    def setUpClass(cls): 
        super().setUpClass() 
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR) 
 
    @classmethod 
    def tearDownClass(cls): 
        super().tearDownClass() 
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True) 
 
    def setUp(self): 
        self.guest_client = Client() 
        self.user = User.objects.create_user(username='TestUser') 
        self.authorized_client = Client() 
        self.authorized_client.force_login(self.user) 
        self.user_maxim = User.objects.create_user(username='Maxim') 
        self.authorized_client_maxim = Client() 
        self.authorized_client_maxim.force_login(self.user_maxim) 
        self.user_uri = User.objects.create_user(username='Uri') 
        self.authorized_client_uri = Client() 
        self.authorized_client_uri.force_login(self.user_uri) 
        self.group = Group.objects.create( 
            title='leo', 
            slug='leo', 
            description='leo' 
        ) 
        self.post = Post.objects.create( 
            text="Test post", 
            group=self.group, 
            author=self.user 
        ) 
        self.count_follow = Follow.objects.count() 
        self.count_post = Post.objects.count() 
 
    def test_pages_uses_correct_template(self): 
        templates_pages_names = { 
            reverse('index'): 'index.html', 
            reverse('group', kwargs={'slug': self.group.slug}): 'group.html', 
            reverse('new_post'): 'form.html', 
            reverse( 
                'post_edit', 
                kwargs={ 
                    'username': self.user.username, 
                    'post_id': self.post.pk 
                } 
            ): 'form.html', 
        } 
        for reverse_name, template in templates_pages_names.items(): 
            with self.subTest(template=template): 
                response = self.authorized_client.get(reverse_name) 
                self.assertTemplateUsed(response, template) 
 
    def test_new_show_correct_context(self): 
        """Шаблон new сформирован с правильным контекстом.""" 
        response = self.authorized_client.get(reverse('new_post')) 
        form_fields = { 
            'text': forms.fields.CharField, 
            'group': forms.fields.ChoiceField, 
        } 
        for value, expected in form_fields.items(): 
            with self.subTest(value=value): 
                cache.clear() 
                form_field = response.context.get('form').fields.get(value) 
                self.assertIsInstance(form_field, expected) 
 
    def test_post_edit_show_correct_context(self): 
        form_fields = { 
            'text': forms.fields.CharField, 
            'group': forms.fields.ChoiceField, 
        } 
        response = self.authorized_client.get(reverse( 
            'post_edit', 
            kwargs={'username': self.user, 'post_id': self.post.pk} 
        )) 
        for value, expected in form_fields.items(): 
            with self.subTest(value=value): 
                form_field = response.context.get('form').fields.get(value) 
                self.assertIsInstance(form_field, expected) 
 
    def test_index_correct_context(self): 
        """Шаблон index сформирован с правильным контекстом.""" 
        cache.clear() 
        response = self.authorized_client.get(reverse('index')) 
        post = response.context.get('page')[0] 
        self.assertEqual(post.text, 'Test post') 
        self.assertEqual(post.author, self.user) 
        self.assertEqual(post.group, self.group) 
 
    def test_index_cache(self): 
        response = self.authorized_client.get(reverse('index')) 
        count = self.count_post 
        Post.objects.create( 
            text='This is a test', 
            author=self.user 
        ) 
        post = response.context.get('page') 
        self.assertEqual(len(post), count) 
        cache.clear() 
        response = self.authorized_client.get(reverse('index')) 
        post = response.context.get('page') 
        self.assertEqual(len(post), count + 1) 
 
    def test_index_image(self): 
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
        Post.objects.create( 
            text='This is a test', 
            author=self.user, 
            group=self.group, 
            image=uploaded 
        ) 
        cache.clear() 
        response = self.authorized_client.get(reverse('index')) 
        posts = response.context.get('page').object_list 
        self.assertListEqual(list(posts), list(Post.objects.all()[:10])) 
 
    def test_group_image(self): 
        group_max = Group.objects.create( 
            title='maxim', 
            slug='max', 
            description='maxim = maximum' 
        ) 
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
        Post.objects.create( 
            text='This is a test', 
            author=self.user_maxim, 
            group=group_max, 
            image=uploaded 
        ) 
        response = self.authorized_client.get( 
            reverse( 
                'group', 
                kwargs={ 
                    'slug': group_max.slug 
                } 
            ) 
        ) 
        post = response.context.get('page').object_list 
        self.assertListEqual( 
            list(post), 
            list( 
                Post.objects.filter( 
                    author=self.user_maxim.id 
                ) 
            ) 
        ) 
 
    def test_profile_image(self): 
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
        Post.objects.create( 
            text='This is a test', 
            author=self.user_maxim, 
            image=uploaded 
        ) 
        response = self.authorized_client.get( 
            reverse( 
                'profile', 
                kwargs={ 
                    'username': self.user_maxim 
                } 
            ) 
        ) 
        post = response.context.get('page').object_list 
        self.assertListEqual( 
            list(post), 
            list( 
                Post.objects.filter( 
                    author=self.user_maxim.id 
                ) 
            ) 
        ) 
 
    def test_post_image(self): 
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
        post = Post.objects.create( 
            text='This is a test', 
            author=self.user, 
            group=self.group, 
            image=uploaded 
        ) 
        response = self.authorized_client.get( 
            reverse( 
                'post', 
                kwargs={ 
                    'username': self.user, 
                    'post_id': post.pk 
                } 
            ) 
        ) 
        post_context = response.context['post_list'] 
        self.assertEqual(post_context.text, post.text) 
        self.assertEqual(post_context.author, self.user) 
        self.assertEqual(post_context.group, self.group) 
        self.assertEqual(post_context.image, post.image) 
 
    def test_post_correct_context(self): 
        """Шаблон post сформирован с правильным контекстом.""" 
        response = self.authorized_client.get( 
            reverse( 
                'post', 
                kwargs={'username': self.user, "post_id": self.post.id} 
            ) 
        ) 
        post = response.context['post_list'] 
        self.assertEqual(post.text, 'Test post') 
        self.assertEqual(post.author, self.user) 
        self.assertEqual(post.group, self.group) 
 
    def test_profile_correct_context(self): 
        """Шаблон profile сформирован с правильным контекстом.""" 
        response = self.authorized_client.get(reverse( 
            'profile', 
            kwargs={'username': self.user} 
        )) 
        post = response.context.get('page')[0] 
        self.assertEqual(post, self.post) 
 
    def test_profile_correct_count_posts(self): 
        for i in range(15): 
            Post.objects.create( 
                text='This is a test', 
                author=self.user, 
                group=self.group 
            ) 
        cache.clear() 
        response = self.authorized_client.get(reverse( 
            'index' 
        )) 
        posts = response.context.get('page').object_list 
        self.assertListEqual(list(posts), list(Post.objects.all()[:10])) 
        response = self.authorized_client.get('/?page=2') 
        posts = response.context.get('page').object_list 
        self.assertListEqual(list(posts), list(Post.objects.all()[10:])) 
 
    def test_index_correct_count_posts(self): 
        for i in range(15): 
            Post.objects.create( 
                text='This is a test', 
                author=self.user, 
                group=self.group 
            ) 
        cache.clear() 
        response = self.authorized_client.get(reverse( 
            'index' 
        )) 
        posts = response.context.get('page').object_list 
        self.assertListEqual(list(posts), list(Post.objects.all()[:10])) 
        response = self.authorized_client.get('/?page=2') 
        posts = response.context.get('page').object_list 
        self.assertListEqual(list(posts), list(Post.objects.all()[10:])) 
 
    def test_group_post(self): 
        group_second = Group.objects.create( 
            title='test', 
            slug='test', 
            description='test group' 
        ) 
        Post.objects.create( 
            text="Test", 
            group=group_second, 
            author=self.user 
        ) 
        response = self.authorized_client.get( 
            reverse( 
                'group', 
                kwargs={'slug': group_second} 
            ) 
        ) 
        post = response.context.get('page')[0] 
        self.assertEqual(post.text, 'Test') 
        self.assertEqual(post.author, self.user) 
        self.assertEqual(post.group, group_second) 
 
    def test_group_post_not_in_second(self): 
        group_second = Group.objects.create( 
            title='test', 
            slug='test', 
            description='test group' 
        ) 
        Post.objects.create( 
            text="Test", 
            group=group_second, 
            author=self.user 
        ) 
        response = self.authorized_client.get( 
            reverse( 
                'group', 
                kwargs={'slug': group_second} 
            ) 
        ) 
        response_second = self.authorized_client.get( 
            reverse( 
                'group', 
                kwargs={'slug': self.group} 
            ) 
        ) 
        posts = response.context.get('page').object_list 
        posts_second = response_second.context.get('page').object_list 
        post = response.context.get('page')[0] 
        self.assertNotEqual(post.text, self.post.text) 
        self.assertNotEqual(post.group, self.group) 
        self.assertNotEqual(posts, posts_second) 
 
    def test_follow_index(self): 
        Post.objects.create( 
            text='maxim post', 
            author=self.user_maxim 
        ) 
        Follow.objects.create(user=self.user_maxim, author=self.user) 
        response = self.authorized_client_maxim.get(reverse('follow_index')) 
        posts = response.context.get('page').object_list 
        self.assertListEqual( 
            list(posts), 
            list(Post.objects.filter(author=self.user.id)[:10]) 
        ) 
 
    def test_follow_index_not_behind_posts(self): 
        Post.objects.create( 
            text='maxim post', 
            author=self.user_maxim 
        ) 
        Follow.objects.create(user=self.user_maxim, author=self.user) 
        response_2 = self.authorized_client_uri.get(reverse('follow_index')) 
        posts_2 = response_2.context.get('page').object_list 
        self.assertListEqual( 
            list(posts_2), 
            list(Post.objects.filter(author=self.user.id)[2:]) 
        ) 
 
    def test_follow_author_and_unfollow(self): 
        Post.objects.create( 
            text='maxim post', 
            author=self.user_maxim 
        ) 
        self.authorized_client.get( 
            F'/{self.user_maxim.username}/follow/' 
        ) 
        count_following = Follow.objects.all().count() 
        self.assertEqual(count_following, self.count_follow + 1) 
        self.authorized_client.get( 
            F'/{self.user_maxim.username}/unfollow/' 
        ) 
        self.assertEqual(Follow.objects.count(), count_following - 1) 
 
    def test_follow_author_and_unfollow(self): 
        Post.objects.create( 
            text='maxim post', 
            author=self.user_maxim 
        ) 
        Follow.objects.create(user=self.user, author=self.user_maxim) 
        count_following = Follow.objects.all().count() 
        self.authorized_client.get( 
            F'/{self.user_maxim.username}/unfollow/' 
        ) 
        self.assertEqual(Follow.objects.count(), count_following - 1)
