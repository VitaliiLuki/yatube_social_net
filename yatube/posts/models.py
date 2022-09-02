from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Имя автора',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        'Group',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self) -> str:
        return self.text[:15]

    class Meta:
        ordering = ("-pub_date",)


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название группы',
        max_length=200
    )
    slug = models.SlugField(
        verbose_name='Уникальное имя',
        unique=True)
    description = models.TextField(verbose_name='Краткое описание группы')

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )
    created = models.DateTimeField(
        verbose_name='Дата и время отправки комментария',
        auto_now_add=True
    )

    class Meta:
        ordering = ("-created",)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="already_following"
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F("user")),
                name="not_self_follow"
            )
        ]
