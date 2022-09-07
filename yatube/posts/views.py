from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Group, Post, User, Follow

NUMBER_OF_DISPLAYED_ITEMS: int = 10
TIMEOUT_FOR_CACHE: int = 20


def paginator(post_list, request):
    """Пагинация постов"""
    paginator = Paginator(post_list, NUMBER_OF_DISPLAYED_ITEMS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(TIMEOUT_FOR_CACHE, key_prefix='index')
def index(request):
    """Главная страница проекта"""
    page_title = 'Это главная страница проекта Yatube'
    post_list = Post.objects.all()
    context = {
        'page_title': page_title,
        'page_obj': paginator(post_list, request),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Просмотр всех постов выбранной группы"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'group': group,
        'page_obj': paginator(post_list, request),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Страничка профиля"""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author')
    following = author.following.filter(user__id=request.user.id).exists()
    context = {
        'request': request,
        'author': author,
        'page_obj': paginator(post_list, request),
        'count': author.posts.count(),
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Просмотр отдельного поста"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required(login_url='users:login')
def post_create(request):
    """Создание нового поста"""
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    # Если сделать условие в стиле "if not form.is_valid()""
    # и сразу редирект, то сохранение формы сдвигается левее.
    # В таком случае не совсем понятно как выполнить return render
    # шаблона и формы, а также return редирект после сохранения
    # формы. Пробовал объединить - не вышло.
    # Буду благодарен за пояснение, комментарий потом удалю.
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user)
    return render(request, template, {'form': form})


@login_required(login_url='users:login')
def post_edit(request, post_id):
    """Редактирование поста"""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(
        request,
        template,
        {'form': form, 'post': post, 'is_edit': True}
    )


@login_required(login_url='users:login')
def add_comment(request, post_id):
    """Добавление комментариев к постам"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required(login_url='users:login')
def follow_index(request):
    """Страница интересных авторов"""
    post_list = Post.objects.filter(author__following__user=request.user)
    template = 'posts/follow.html'
    context = {
        'page_obj': paginator(post_list, request),
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def profile_follow(request, username):
    """Подписка на интересных авторов"""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect('posts:profile', username=username)


@login_required(login_url='users:login')
def profile_unfollow(request, username):
    """Отписка от авторов"""
    Follow.objects.filter(
        user=request.user,
        author=User.objects.filter(username=username)[0]
    ).delete()
    return redirect('posts:profile', username=username)
