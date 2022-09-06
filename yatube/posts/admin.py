from django.contrib import admin

from .models import Comment, Group, Post


class PostAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    # Добавляем интерфейс для поиска по тексту постов
    search_fields = ('text',)
    # Добавляем возможность фильтрации по дате
    list_filter = ('pub_date', 'group')
    empty_value_display = '-пусто-'
    list_editable = ('group',)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'created', 'post', 'text')
    list_filter = ('author', 'created')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
