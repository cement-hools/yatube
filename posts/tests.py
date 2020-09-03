from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from .models import Group, Post, User


class TestUser(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah", 
            email="connor.s@skynet.com", 
            password="12345"
        )
        self.group = Group.objects.create(
            title="Test group", 
            slug="testgroup",
            description="Test Group"
        )  
        self.post = Post.objects.create(
            text=("You're talking about things I haven't done yet" 
            "in the past tense. It's driving me crazy!"), 
            author=self.user, 
            group=self.group
        )
        self.login_client = Client()
        self.login_client.force_login(self.user)
                 
    def add_new_post(self, text):
        """Добавление нового поста"""
        response = self.login_client.post(
            reverse("new_post"),
            {"text": text, "group": self.group.id},
            follow=True
        )
        return response
    
    def checking_text_in_pages(self, text, url_list):
        """Проверка содержится ли текст на страницах из списка"""
        for url in url_list:
            response = self.client.get(url)
            self.assertContains(response, text)

    def edit_post(self, text):
        """Авторизованный пользователь редактирует свой пост"""
        response = self.login_client.post(
            reverse("post_edit", 
            args=["sarah", 1]),
            {"text": text},
            follow=True
        )
        return response

    def test_profile(self):
        """Наличие страницы профиля"""
        # формируем GET-запрос к странице сайта
        response = self.client.get(reverse("profile", args=["sarah"]))
        # проверяем что страница найдена
        self.assertEqual(response.status_code, 200)

    def test_new_login_user(self):
        """Авторизованный пользователь может создать свой пост"""
        post_text = "test post"
        response = self.add_new_post(post_text)
        self.assertEqual(response.status_code, 200)

    def test_new_nonlogin_user(self):
        """Не авторизованный пользователь при создании поста переходит на страницу авторизации"""
        response = self.client.get(reverse("new_post"), follow=True)
        auth_url = reverse("login")
        new_post_url = reverse("new_post")
        redirect = f"{auth_url}?next={new_post_url}"
        self.assertRedirects(response, redirect) 

    def test_edit_post(self):
        """Проверка, что авторизованный пользователь может отредактировать свой пост"""
        post_text = "test post edit"
        response = self.edit_post(post_text)
        self.assertRedirects(response, reverse("post", args=["sarah", 1]))

    def test_add_new_post(self):
        """После публикации поста новая запись появляется на главной странице сайта (index)"""
        post_text = "test post"
        response = self.add_new_post(post_text)
        self.assertRedirects(response, reverse("index"))
    
    def test_new_post_in_all_pages(self):
        """После публикации поста новая запись появляется на всех связанных страницах"""    
        post_text = "test post"
        url_list = [
            reverse("index"),
            reverse("profile", args=["sarah"]),
            reverse("post", args=["sarah", 2]),
        ]
        self.add_new_post(post_text)        
        self.checking_text_in_pages(post_text, url_list)

    def test_edit_post_in_all_pages(self):
        """Проверка отредактированного текста на всех связанных страницах"""
        post_text = "test post edit"
        url_list = [
            reverse("index"),
            reverse("profile", args=["sarah"]),
            reverse("post", args=["sarah", 1]),
        ]
        self.edit_post(post_text)
        self.checking_text_in_pages(post_text, url_list)

    def test_404_page(self):
        """возвращает ли сервер код 404, если страница не найдена."""
        response = self.client.get("/404/")
        self.assertEqual(response.status_code, 404) 

    def test_img_in_post_page(self):
        """проверяют страницу конкретной записи с картинкой: на странице есть тег <img>"""
        # response = self.login_client.post(
        #     reverse("new_post"),
        #     {
        #         "text": "post with image",
        #         "group": self.group.id,
        #         "image": "posts/file.jpg"
        #         },
        #     follow=True
        # )
        # post_img = Post.objects.create(
        #     text=("post with image"), 
        #     author=self.user, 
        #     group=self.group,
        #     image="posts/file.jpg",
        # )
        post_text = "test post"
        url_list = [
            reverse("index"),
            reverse("profile", args=["sarah"]),
            reverse("post", args=["sarah", 5]),
        ]
        response = self.login_client.post(
            reverse("new_post"),
            {"text": post_text, "group": self.group.id, "image": "posts/file.jpg"}, 
            follow=True
        )       
        self.checking_text_in_pages("post_textvcb", url_list)
        

    def test_img_in_index_page(self):
        """проверяют, что на главной странице  пост с картинкой отображается корректно, с тегом <img>"""
        pass

    def test_img_in_post_page(self):
        """проверяют, что срабатывает защита от загрузки файлов не-графических форматов"""
        pass
