import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow


def page_not_found(request, exception):
    """Страница не найдена"""
    # Переменная exception содержит отладочную информацию, 
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    """Ошибка сервера"""
    return render(request, "misc/500.html", status=500)

@cache_page(20)
def index(request):
    """Главная страница"""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get("page")  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    context = {"page": page, "paginator": paginator}
    return render(request, "index.html", context)


def group_posts(request, slug):
    """Все посты выбранной группы"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(
        request, 
        "group.html", 
        {"group": group, "page": page, "paginator": paginator}
        )


def profile(request, username):
    """Страница профиля"""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    my_user = request.user
    #following = Follow.objects.filter(user=my_user, author=author)
    following = Follow.objects.filter(author=author).count()
    follower = Follow.objects.filter(user=author).count()
    context = {
        "author": author,
        "page": page,
        "paginator": paginator,
        "posts": post_list,
        "following": following,
        "follower": follower,
        }
    return render(request, "profile.html", context)

 
def post_view(request, username, post_id):
    """Просмотр поста"""
    post = Post.objects.get(id=post_id)
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    len_posts = len(post_list)
    form = CommentForm(request.POST or None)
    items = post.comments.all()
    context = {
        "username": post.author,
        "post": post,
        "len_posts": len_posts,
        "form": form,
        "items": items,
        }
    return render(request, "post.html", context)


@login_required
def post_edit(request, username, post_id):
    """Не забудьте проверить, что текущий пользователь — это автор записи.
    В качестве шаблона страницы редактирования укажите шаблон создания новой записи
    который вы создали раньше (вы могли назвать шаблон иначе)"""
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None, 
        files=request.FILES or None, 
        instance=post
    )
    if post.author != request.user:
        return redirect(f"/{username}/{post_id}/")
    if form.is_valid():
        form.save()
        return redirect(f"/{username}/{post_id}/")
    return render(request, "new_post.html", {"form": form, "post": post})


@login_required
def new_post(request):
    """Создание нового поста"""
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")
    return render(request, "new_post.html", {"form": form})


def add_comment(request, username, post_id):
    """Добавление комментария"""
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("post", username=username, post_id=post_id)
    return redirect("post", username=username, post_id=post_id)    
    

@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    # following = request.user.follower.all()
    # following_list=[item.author for item in following]
    # post_list = Post.objects.filter(author__in=following_list)
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get("page")  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    context = {"page": page, "paginator": paginator}
    return render(request, "follow.html", context)

@login_required
def profile_follow(request, username):
    my_user = request.user
    my_author = get_object_or_404(User, username=username)
    authors = Follow.objects.filter(user=my_user, author=my_author)
    if authors.exists() or my_user == my_author:
        return redirect("profile", username=username)
    Follow.objects.create(user=my_user, author=my_author)    
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    my_user = request.user
    my_author = get_object_or_404(User, username=username)
    authors = Follow.objects.filter(user=my_user, author=my_author)
    if authors.exists():
        authors.delete()
        return redirect("profile", username=username)
    return redirect("profile", username=username)



def posts_in_range_date(request):
    """РЕВЬЮЕР НЕ ОБРАЩАЙ ВНИМАНИЕ НА ЭТУ ФУНКЦИЮ (Это для примера) 
    Функция для проверки поиска по ключевому слову и календарному интервалу"""
    author = get_object_or_404(User, username="leo")
    keyword = "утро"
    start_date = datetime.date(1854, 7, 7)
    end_date = datetime.date(1854, 7, 21)
    posts = Post.objects.filter(
        text__icontains=keyword,
        pub_date__range=(start_date, end_date),
        author=author,
    )
    return render(request, "index.html", {"posts": posts})


def search(request):
    """Поиск по тексту постов"""
    keyword = request.GET.get("q", None)
    posts = Post.objects.select_related("author", "group").all()
    if keyword:
        posts = posts.filter(text__icontains=keyword)      
    else:
        posts = posts.none()
    return render(request, "search.html", {"posts": posts, "keyword": keyword})    
