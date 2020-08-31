from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ("group", "text", "image")  
        labels = {"text": "Введите текст", "group": "Выберите группу"}
        help_texts = {"text": "Текст поста", "group": "Из уже существующих"}  
        