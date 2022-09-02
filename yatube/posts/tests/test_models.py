from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='Teстовый slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст на проверку _str_',
            group=cls.group
        )

    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_text = self.post.text[:15]
        self.assertEqual(expected_text, str(self.post))

    def test_model_group_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_title = self.post.group.title
        self.assertEqual(expected_title, str(self.post.group))

    def test_models_has_verbose_names(self):
        """Проверяем verbose_names  у моделей"""
        verbose_names_for_fields = {
            ('text', self.post, 'Текст поста'),
            ('pub_date', self.post, 'Дата публикации'),
            ('author', self.post, 'Имя автора'),
            ('group', self.post, 'Группа'),
            ('title', self.post.group, 'Название группы'),
            ('slug', self.post.group, 'Уникальное имя'),
            ('description', self.post.group, 'Краткое описание группы'),
        }
        for field, data, verbose in verbose_names_for_fields:
            with self.subTest(field=field):
                verbose_name = data._meta.get_field(field).verbose_name
                self.assertEqual(verbose_name, verbose)

    def test_models_has_help_texts(self):
        """Проверяем help_texts у моделей"""
        help_texts = [
            ('text', 'Текст нового поста'),
            ('group', 'Группа, к которой будет относиться пост'),
        ]
        for field, help_text in help_texts:
            with self.subTest(field=field):
                verbose_name = self.post._meta.get_field(field).help_text
                self.assertEqual(verbose_name, help_text)
