from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse

from .models import Post, Group, User

import datetime


def index(request):
    latest = Post.objects.order_by("-pub_date")[:11]
    return render(request, "index.html", {"posts": latest})

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:12]
    return render(request, "group.html", {"group": group, "posts": posts})

def test(request):
    author = User.objects.get(username="leo")
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
        posts = posts.filter(text__contains=keyword)      
    else:
        posts = None

    return render(request, "search.html", {"posts": posts, "keyword": keyword})    
