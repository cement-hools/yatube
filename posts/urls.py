from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("group/<slug:slug>/", views.group_posts, name="group"),
    path("posts_in_range_date/", views.posts_in_range_date, name="test"),
    path("search/", views.search, name="search"),
    path("new/", views.new_post, name="new_post"),
    # path("404/", views.page_not_found, name="page_not_found"),
    # path("500/", views.server_error, name="server_error"),
    # Профайл пользователя
    path("<str:username>/", views.profile, name="profile"),
    # Просмотр записи
    path("<str:username>/<int:post_id>/", views.post_view, name="post"),
    path(
        "<str:username>/<int:post_id>/edit/", 
        views.post_edit, 
        name="post_edit"
    ), 
    path("<username>/<int:post_id>/comment", 
        views.add_comment, 
        name="add_comment"
        ),   
]
