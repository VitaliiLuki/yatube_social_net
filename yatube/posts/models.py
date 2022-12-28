from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Comment(models.Model):
    """Stores a comments to a posts."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date and time the comment was sent'
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        help_text='Input comment text',
        verbose_name='Text of comment',
    )

    class Meta:
        ordering = ("-created",)


class Follow(models.Model):
    """Stores a subscriptions of user."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Who is subscribe to',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Follower',
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
    """Stores the unique groups."""
    description = models.TextField(
        verbose_name='Short group description'
    )
    slug = models.SlugField(
        verbose_name='Unique name',
        unique=True
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Group name',
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    """Stores all information about posts."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Name of author',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        help_text='Group which post is related to',
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Group',
    )
    image = models.ImageField(
        blank=True,
        upload_to='posts/',
        verbose_name='Image',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication date',
    )
    text = models.TextField(
        help_text='New text of post',
        verbose_name='Text of post',
    )

    def __str__(self) -> str:
        return self.text[:15]

    class Meta:
        ordering = ("-pub_date",)
