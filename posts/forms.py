from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ("group", "text", "image")  
        labels = {
            "text": "Введите текст", 
            "group": "Выберите группу", 
            "image": "Изображение"
            }
        help_texts = {
            "text": "Текст поста", 
            "group": "Из уже существующих",
            "image": "Выберите изображение"
            }  

class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 10}))
    
    class Meta:
        model = Comment
        fields = ("text",)  
