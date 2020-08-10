import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    latest = Post.objects.all()[:11]
    return render(request, "index.html", {"posts": latest})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:12]
    return render(request, "group.html", {"group": group, "posts": posts})


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")
    form = PostForm()    
    return render(request, "new_post.html", {"form": form})


def test(request):
    author = get_object_or_404(User, username="leo")
    keyword = "утро"
    start_date = datetime.date(1854, 7, 7)
    end_date = datetime.date(1854, 7, 21)
    posts = Post.objects.filter(
        text__contains=keyword
        ).filter(
        pub_date__range=(start_date, end_date)
        ).filter(
            author=author
        )
    return render(request, "index.html", {"posts": posts})


def search(request):
    keyword = request.GET.get("q", None)
    posts = Post.objects.select_related("author", "group").all()
    if keyword:
        posts = posts.filter(text__icontains=keyword)      
    else:
        posts = None
    return render(request, "search.html", {"posts": posts, "keyword": keyword})    
