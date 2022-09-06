import shutil
import tempfile
from multiprocessing.connection import Client
from random import randint

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateEditFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group,
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    def check_for_post_existence(self, source_post, form_data, uploaded):
        self.assertEqual(source_post.text, form_data['text'])
        self.assertEqual(source_post.author, self.user)
        self.assertEqual(source_post.group, self.group)
        self.assertEqual(source_post.image.name, f'posts/{uploaded.name}')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Проверка создания нового поста на странице '/create/'."""
        old_post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name=f'{randint(1,99)}small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Какой-то тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={
                    'username': PostCreateEditFormTests.post.author
                }
            )
        )
        self.assertEqual(Post.objects.count(), (old_post_count + 1))
        new_post = Post.objects.first()
        self.check_for_post_existence(new_post, form_data, uploaded)

    def test_сreate_post_for_unauthorized(self):
        """Проверка создания поста неавторизированным пользователем"""
        old_post_count = Post.objects.count()
        form_data = {
            'text': 'Какой-то тестовый текст',
            'group': self.group.id,
        }
        self.client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertEqual(old_post_count, Post.objects.count())

    def test_post_edit(self):
        """
        Проверка отправки валидной формы и создания нового поста
        """
        old_post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name=f'{randint(100,199)}small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Какой-то тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.post.id
                }
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), old_post_count)
        edited_post = Post.objects.get(id=self.post.id)
        self.check_for_post_existence(edited_post, form_data, uploaded)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': self.post.id
                }
            )
        )
