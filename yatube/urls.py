from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path

urlpatterns = [
    # flatpages
    path("about/", include('django.contrib.flatpages.urls')),
    path('about-author/', views.flatpage, {'url': '/about-author/'}, 
         name='about-author'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, 
         name='about-spec'),
    path('contacts/', views.flatpage, {'url': '/contacts/'}, 
          name='contacts'),     
    #  регистрация и авторизация
    path("auth/", include("users.urls")),
    #  если нужного шаблона для /auth не нашлось в файле users.urls — 
    #  ищем совпадения в файле django.contrib.auth.urls
    path("auth/", include("django.contrib.auth.urls")),
    #  раздел администратора
    path("admin/", admin.site.urls), 
    #  обработчик для главной страницы ищем в urls.py приложения posts
    path("", include("posts.urls")),
]
