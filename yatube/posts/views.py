from django.contrib.auth.decorators import login_required 
from django.core.paginator import Paginator 
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect, 
                              render) 
from django.views.decorators.cache import cache_page 
 
from .forms import CommentForm, PostForm 
from .models import Follow, Group, Post, User 
 
 
@cache_page(1 * 8) 
def index(request): 
    post_list = get_list_or_404(Post) 
    paginator = Paginator(post_list, 10) 
    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number) 
    return render(request, 'index.html', { 
        'page': page, 
        'paginator': paginator, 
    }) 
 
 
@cache_page(1 * 8) 
def group_posts(request, slug): 
    group = get_object_or_404(Group, slug=slug) 
    post_list = group.posts.all() 
    paginator = Paginator(post_list, 10) 
    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number) 
    posts_count = post_list.count() 
    context = { 
        'group': group, 
        'page': page, 
        'paginator': paginator, 
        'count': posts_count 
    } 
    return render(request, 'group.html', context) 
 
 
@login_required 
def new_post(request): 
    commit = False 
    form = PostForm(request.POST or None, files=request.FILES or None) 
    if request.method == 'POST' and form.is_valid(): 
        form.save(commit).author = request.user 
        form.save() 
        return redirect('index') 
    form = PostForm() 
    button = 'Создать новую запись' 
    title = 'Новая запись' 
    header = 'Создание новой записи' 
    context = { 
        'form': form, 
        'button': button, 
        'title': title, 
        'header': header 
    } 
    return render(request, "form.html", context) 
 
 
def profile(request, username): 
    profile = get_object_or_404(User, username=username) 
    post_list = profile.posts.all() 
    posts_count = post_list.count() 
    paginator = Paginator(post_list, 10) 
    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number) 
    following = False 
    if request.user.is_authenticated: 
        following = Follow.objects.filter( 
            user=request.user, 
            author=profile.id 
        ).exists() 
    context = { 
        'profile': profile, 
        'post_list': post_list, 
        'posts_count': posts_count, 
        'page': page, 
        'paginator': paginator, 
        'following': following, 
    } 
    return render(request, 'profile.html', context) 
 
 
def post_view(request, username, post_id): 
    post_list = get_object_or_404(Post, pk=post_id, author__username=username) 
    profile = post_list.author 
    form = CommentForm() 
    comments = post_list.comments.all() 
    following = False 
    if request.user.is_authenticated: 
        following = Follow.objects.filter( 
            user=request.user, 
            author=profile.id 
        ).exists() 
    context = { 
        'post_list': post_list, 
        'profile': profile, 
        'form': form, 
        'comments': comments, 
        'following': following, 
    } 
    return render(request, 'post.html', context) 
 
 
@login_required 
def post_edit(request, username, post_id): 
    post = get_object_or_404(Post, pk=post_id, author__username=username) 
    profile = post.author 
    if request.user != profile: 
        return redirect('post', username=profile.username, post_id=post_id) 
    form = PostForm( 
        request.POST or None, 
        files=request.FILES or None, 
        instance=post 
    ) 
    if form.is_valid(): 
        form.save() 
        return redirect('post', username=profile.username, post_id=post_id) 
    title = 'Редактировать' 
    header = 'Редактирование записи' 
    button = 'Изменить' 
    context = { 
        'form': form, 
        'button': button, 
        'title': title, 
        'post': post, 
        'header': header 
    } 
    return render(request, 'form.html', context) 
 
 
@login_required 
def add_comment(request, username, post_id): 
    post = get_object_or_404(Post, pk=post_id, author__username=username) 
    form = CommentForm(request.POST or None) 
    if form.is_valid(): 
        comment = form.save(commit=False) 
        comment.author = request.user 
        comment.post = post 
        comment.save() 
    return redirect("post", username=username, post_id=post_id) 
 
 
@login_required 
def follow_index(request): 
    post_list = Post.objects.filter(author__following__user=request.user) 
    paginator = Paginator(post_list, 10) 
    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number) 
    context = { 
        'paginator': paginator, 
        'page': page 
    } 
    return render(request, "follow.html", context) 
 
 
@login_required 
def profile_follow(request, username): 
    author = get_object_or_404(User, username=username) 
    if author.username != request.user.username: 
        Follow.objects.get_or_create(user=request.user, author=author) 
    return redirect("profile", username=username) 
 
 
@login_required 
def profile_unfollow(request, username): 
    author = get_object_or_404(User, username=username) 
    Follow.objects.filter(user=request.user, author=author).delete() 
    return redirect("profile", username=username) 
 
 
def page_not_found(request, exception): 
    return render( 
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404 
    ) 
 
 
def server_error(request): 
    return render(request, "misc/500.html", status=500) 
