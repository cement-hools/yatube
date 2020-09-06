from django.contrib import admin

from .models import Post, Group, Comment, Follow

class PostAdmin(admin.ModelAdmin):
    # перечисляем поля, которые должны отображаться в админке
    list_display = ("pk", "text", "pub_date", "author", "group") 
    # добавляем интерфейс для поиска по тексту постов
    search_fields = ("text",) 
    # добавляем возможность фильтрации по дате
    list_filter = ("pub_date",) 
    empty_value_display = "-пусто-" # это свойство сработает для всех колонок: где пусто - там будет эта строка

class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "post", "author", "created") 

# при регистрации модели Post источником конфигурации для неё назначаем класс PostAdmin
admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow)
