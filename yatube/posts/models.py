from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(unique=True, verbose_name='Заголовок группы')
    description = models.TextField(verbose_name='Описание группы')
    rules = models.TextField(
        blank=True,
        null=False,
        verbose_name='Правила группы'
    )

    def __str__(self):
        return self.title[:50]


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст публикации',
        help_text='Введите текст публикации'
    )
    pub_date = models.DateTimeField('date published', auto_now_add=True, db_index=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу публикации'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор публикации'
    )
    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField('date published', auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-created']

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')