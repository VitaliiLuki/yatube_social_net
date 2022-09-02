import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
NUMBER_OF_POSTS = 14
EXSPECTED_AMOUNT_OF_POSTS_FIRST_PAGE = 10
EXSPECTED_AMOUNT_OF_POSTS_SECOND_PAGE = int(
    NUMBER_OF_POSTS - EXSPECTED_AMOUNT_OF_POSTS_FIRST_PAGE
)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='some_user1')
        cls.follower_user = User.objects.create_user(username='follower')
        cls.group = Group.objects.create(
            title='Тестовая группуля',
            slug='Test-slug1',
            description='Тестовый description для тестовой группули',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст1',
            author=cls.user,
            group=cls.group,
        )
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    def setUp(self):
        # Создаем неавторизированных пользователей
        self.guest_client = Client()
        self.authorized_client = Client()
        self.auth_client_follow = Client()
        # Авторизируем пользователей
        self.authorized_client.force_login(PostPagesTests.user)
        self.auth_client_follow.force_login(PostPagesTests.follower_user)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def post_response_context(self, source_post):
        """Соответствие полей из контекста полям из БД конкретного поста"""
        return (
            self.assertEqual(source_post.author, self.user),
            self.assertEqual(source_post.text, self.post.text),
            self.assertEqual(source_post.group.title, self.post.group.title),
        )

    def test_index_page_uses_correct_template(self):
        """URL-адреса использует правильные шаблоны."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.post.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': PostPagesTests.user}):
            'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.id}):
            'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверка контекста 'index' при создания поста с группой."""
        response = self.authorized_client.get(reverse('posts:index'))
        compared_post = response.context['page_obj'][0]
        self.post_response_context(compared_post)

    def test_group_page_show_correct_context(self):
        """Проверка контекста 'group_list' при создания поста с группой."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={
                'slug': PostPagesTests.post.group.slug})
        )
        compared_post = response.context['page_obj'][0]
        self.post_response_context(compared_post)

    def test_profile_page_show_correct_context(self):
        """Проверка контекста 'profile' при создания поста с группой."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': PostPagesTests.post.author.username})
        )
        compared_post = response.context['page_obj'][0]
        self.post_response_context(compared_post)

    def test_post_detail_show_correct_context(self):
        """Проверка контекста 'post_detail'."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={
                'post_id': PostPagesTests.post.id})
        )
        compared_post = response.context['post']
        self.post_response_context(compared_post)

    def test_create_forms(self):
        """Проверка типов полей формы 'post_create'."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in PostPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_forms(self):
        """Проверка типов полей формы 'post_edit'."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={
                'post_id': PostPagesTests.post.id})
        )
        for value, expected in PostPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_page_context_contains_image(self):
        small_gif = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post_whith_image = Post.objects.create(
            text='New test post',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
            image=uploaded,
        )
        urls = [
            reverse('posts:index', None),
            reverse('posts:group_list', kwargs={'slug': PostPagesTests.post.group.slug}),
            reverse('posts:profile', kwargs={'username': PostPagesTests.user}),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.image, f'posts/{uploaded.name}')
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={
                'post_id': post_whith_image.id})
        )
        post_detail_context_with_image = response.context['post']
        self.assertEqual(post_detail_context_with_image.image, f'posts/{uploaded.name}')

    def test_comments_for_authorized_users(self):
        """
        Проверка возможности отправки комментария только для 
        авторизироанного пользователя.
        Проверка наличия коммента на странице поста.
        """
        comment_form = {
            'text': 'Абракадабра'
        }
        # Отправка комментария авторизированным пользователем
        response_for_auth = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': PostPagesTests.post.id}), data=comment_form, 
                )
        # Отправка комментария неавторизированным пользователем
        response_for_guest = self.guest_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': PostPagesTests.post.id}), data=comment_form
                )
        # Проверка редиректа после отправки коммента 
        # авторизированным пользователем
        self.assertRedirects(response_for_auth, reverse(
            'posts:post_detail', kwargs={'post_id': PostPagesTests.post.id}),)
        # Проверка редиректа после попытке написать коммент 
        # неавторизированным пользователем
        self.assertEqual(response_for_guest.status_code, 302)
        # Получение респонса от страницы поста, где был
        # оставлен коммент
        response_for_existent_comment = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={
                'post_id': PostPagesTests.post.id}),
        )
        # Получение контекста из поста, к которому был написан коммент
        context = response_for_existent_comment.context['comments'][0]
        # Проверка соотвествия коммента, полученного из контеста
        # отправленному комменту
        self.assertEqual(context.text, comment_form['text'])


    def test_follow_redir_unauth_user(self):
        response = self.guest_client.get('posts:follow_index')
        self.assertTrue(response.status_code in (301, 302))

    def test_autherised_can_follow(self):
        """Проверяем возможность подписки авторизованного пользователя"""
        followers_count = Follow.objects.count()
        response = self.auth_client_follow.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostPagesTests.user}
            )
        )
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': PostPagesTests.user})
        )
        self.assertEqual(Follow.objects.count(), followers_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=PostPagesTests.follower_user,
                author=PostPagesTests.user,
            ).exists()
        )

    def test_autherised_can_unfollow(self):
        """Проверяем возможность отписки авторизованного пользователя"""
        Follow.objects.create(
            user=PostPagesTests.follower_user,
            author=PostPagesTests.user,
        )
        followers_count = Follow.objects.count()
        response = self.auth_client_follow.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostPagesTests.user}
            )
        )
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': PostPagesTests.user})
        )
        self.assertEqual(Follow.objects.count(), followers_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=PostPagesTests.follower_user,
                author=PostPagesTests.user,
            ).exists()
        )

    def test_created_post_on_follow_page(self):
        """Созданный пост добавлен на страницу подписок"""
        Follow.objects.create(
            user=PostPagesTests.follower_user,
            author=PostPagesTests.user,
        )
        response = self.auth_client_follow.get(
            reverse('posts:follow_index')
        )
        self.assertTrue(PostPagesTests.post in response.context['page_obj'])

    def test_created_post_not_on_unfollow_page(self):
        """Пост неотслеживаемого автора не появляется на страницу подписок"""
        Follow.objects.create(
            user=PostPagesTests.follower_user,
            author=PostPagesTests.user,
        )
        some_new_user = User.objects.create_user(username='Somename')
        some_new_post = Post.objects.create(
            text='Просто обычный пост',
            pub_date='Какая-то дата',
            author=some_new_user,
        )
        response = self.auth_client_follow.get(
            reverse('posts:follow_index')
        )
        self.assertTrue(
            some_new_post not in response.context['page_obj']
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='Some_name')
        cls.group = Group.objects.create(
            title='test_title',
            description='test_description',
            slug='test-slug'
        )
        for i in range(NUMBER_OF_POSTS):
            Post.objects.create(
                text=f'Люблю много одинаковых цифр, например: {i*5}',
                author=cls.author,
                group=cls.group,
            )
        cls.pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.author.username}),
        ]

    def test_first_page_contains_ten_records(self):
        cache.clear()
        """Проверка паджинации на первой странице"""
        for page_name in PaginatorViewsTest.pages_names:
            with self.subTest(page_name=page_name):
                response = self.guest_client.get(page_name)
                self.assertEqual(
                    len(response.context.get('page_obj')),
                    EXSPECTED_AMOUNT_OF_POSTS_FIRST_PAGE
                )

    def test_second_page_contains_four_records(self):
        """Проверка паджинации на второй странице"""
        for page_name in PaginatorViewsTest.pages_names:
            with self.subTest(page_name=page_name):
                response = self.guest_client.get((page_name) + '?page=2')
                self.assertEqual(
                    len(response.context.get('page_obj')),
                    EXSPECTED_AMOUNT_OF_POSTS_SECOND_PAGE
                )
