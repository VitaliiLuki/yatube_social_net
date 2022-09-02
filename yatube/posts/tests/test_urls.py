from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='some_username')
        cls.post_author = User.objects.create_user(username='post_author')
        cls.group = Group.objects.create(
            title='Тестовая группуля',
            slug='Test-slug',
            description='Тестовый description для тестовой группули',
        )
        cls.post = Post.objects.create(
            author=cls.post_author,
            text='Тестовый текст тестового поста',
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторезированный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = PostURLTests.user
        # Создаем авторезированный клиент
        self.authorized_client = Client()
        # Авторезируем пользователя
        self.authorized_client.force_login(self.user)
        # Создаем автора
        self.author_client = Client()
        self.author_client.force_login(self.post.author)

    def test_urls_exists_at_desired_location_no_authorized(self):
        """Проверка доступа к страницам для неавторизированных пользователей"""
        urls_available_for_any_users = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.post.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.user}),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.id}),
        ]
        for address in urls_available_for_any_users:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location_authorized(self):
        """Проверка доступа к страницам для авторизированных пользователей"""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_post_edit_for_author(self):
        """Проверка доступа только автору к странице редактирования поста"""
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={
                'post_id': PostURLTests.post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous(self):
        """Проверка перенаправления анонимного пользователя
        со страниц /create/, /posts/<int:post_id>/edit/ на /auth/login/."""
        urls_redirect_anonymous_user = {
            reverse('posts:post_create'): '/auth/login/?next=/create/',
            reverse('posts:post_edit', kwargs={
                'post_id': PostURLTests.post.id}):
            f'/auth/login/?next=/posts/{PostURLTests.post.id}/edit/',
        }
        for address, redirect_address in urls_redirect_anonymous_user.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(
                    response, redirect_address
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.post.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': PostURLTests.user}):
            'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={
                'post_id': PostURLTests.post.id})
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_url_of_non_existent_page(self):
        """Проверка ответа от несуществующей страницы"""
        response = self.guest_client.get('/non_existent/')
        self.assertTemplateUsed(response, 'core/404.html')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
