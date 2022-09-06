from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
        
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время отправки комментария'
        
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        help_text='Введите текст комментария',
        verbose_name='Текст комментария',
    )

    class Meta:
        ordering = ("-created",)


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
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


class Group(models.Model):
    description = models.TextField(
        verbose_name='Краткое описание группы'
    )
    slug = models.SlugField(
        verbose_name='Уникальное имя',
        unique=True
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Имя автора',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        help_text='Группа, к которой будет относиться пост',
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
    )
    image = models.ImageField(
        blank=True,
        upload_to='posts/',
        verbose_name='Картинка',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    text = models.TextField(
        help_text='Текст нового поста',
        verbose_name='Текст поста',
    )

    def __str__(self) -> str:
        return self.text[:15]

    class Meta:
        ordering = ("-pub_date",)











