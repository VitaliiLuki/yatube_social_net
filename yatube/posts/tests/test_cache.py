from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from random import randint as r

from ..models import Group, Post, User


class TestCacheIndex(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='some_user1')
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

    def setUp(self):
        self.client = Client()
        self.client.force_login(TestCacheIndex.user)

    def test_index_saves_cache(self):
        """Проверка кеширования главной страницы."""
        count_posts_before_add_new = Post.objects.count()
        one_extra_post = Post.objects.create(
            text=f'Тестовый пост №{r(1,100)}',
            author=TestCacheIndex.user,
            group=TestCacheIndex.group,
        )
        # Получаем респонс после создания "one_extra_post"
        response = self.client.get(reverse('posts:index'))
        # Получаем контекст после создания "one_extra_post"
        context = response.context['page_obj'][0]
        # Сравниваем поле полученного контекста с полем 
        # созданного поста
        self.assertEqual(context.text, one_extra_post.text)
        # Считаем общее кол-во постов в базе
        count_aftee_add_extra_post= Post.objects.count()
        # Проверяем, что количество постов после создания
        # нового увеличилось на '1'
        self.assertEqual(count_posts_before_add_new + 1, count_aftee_add_extra_post)
        # Удаляем пост
        one_extra_post.delete()
        # Делаем новый запрос к главной странице
        response_cached = self.client.get(reverse('posts:index'))
        # Проверяем, что количество постов после удаления уменьшилось на '1'
        self.assertEqual(Post.objects.count(), count_aftee_add_extra_post - 1)
        # Проверяем контент до и после удаления поста
        self.assertEqual(response.content, response_cached.content)
        cache.clear()
        # Делаем новый запрос после чистки кеша
        response_cleared = self.client.get(reverse('posts:index'))
        # Сравниваем контент до удаления поста и после чистки кеша
        self.assertNotEqual(response.content, response_cleared.content)