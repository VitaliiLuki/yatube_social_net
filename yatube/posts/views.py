from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, get_list_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Group, Post, User, Follow

NUMBER_OF_DISPLAYED_ITEMS: int = 10


def paginator(post_list, request):
    paginator = Paginator(post_list, NUMBER_OF_DISPLAYED_ITEMS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


# Главная страница проекта
@cache_page(20, key_prefix='index')
def index(request):
    text = 'Это главная страница проекта Yatube'
    post_list = Post.objects.all()
    context = {
        'text': text,
        'page_obj': paginator(post_list, request),
    }
    return render(request, 'posts/index.html', context)


# Просмотр всех постов выбранной группы
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'group': group,
        'page_obj': paginator(post_list, request),
    }
    return render(request, 'posts/group_list.html', context)


# Страничка профиля
def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author').order_by('-pub_date')
    count = author.posts.count()
    following = False
    if request.user.is_authenticated:
        following = (Follow.objects.filter(
            user=request.user,
            author=User.objects.filter(username=username)[0]).exists)
    context = {
        'author': author,
        'page_obj': paginator(post_list, request),
        'count': count,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


# Просмотр отдельного поста
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    username = post.author.username
    number_of_posts = post.author.posts.count()
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm()
    context = {
        'post': post,
        'username': username,
        'title': str(post),
        'number_of_posts': number_of_posts,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


# Создание нового поста
@login_required(login_url='users:login')
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST':
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', request.user)
    return render(request, template, {'form': form})


# Редактирование поста
@login_required(login_url='users:login')
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    return render(request, template, {
        'form': form,
        'post': post,
        'is_edit': True}
    )

# Добавление комментариев к постам
@login_required(login_url='users:login')
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


# Страница интересных авторов
@login_required(login_url='users:login')
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    template = 'posts/follow.html'
    context = {
        'page_obj': paginator(post_list, request),
    }
    return render(request, template, context)


# Подписк на интересных авторов
@login_required(login_url='users:login')
def profile_follow(request, username):
    try:
        Follow.objects.create(
            user=request.user,
            author=User.objects.filter(username=username)[0]
        )
    except IntegrityError:
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)


# Отприска от авторов
@login_required(login_url='users:login')
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=User.objects.filter(username=username)[0]
    ).delete()
    return redirect('posts:profile', username=username)
