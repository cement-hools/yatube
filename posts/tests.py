from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from .models import Group, Post, User



# class TestStringMethods(TestCase):
#     def test_length(self):
#         self.assertEqual(len('yatube'), 6)

#     def test_show_msg(self):
#         # действительно ли первый аргумент — True?
#         self.assertTrue(True, msg="Важная проверка на истинность")


class TestUser(TestCase):
    def setUp(self):
        self.client = Client() 
        self.user = User.objects.create_user(
                        username="sarah", email="connor.s@skynet.com", 
                        password="12345"
            )
        self.group = Group.objects.create(title="Test group", slug="testgroup",
                                          description="Test Group")  
        self.post = Post.objects.create(
                        text=("You're talking about things I haven't done yet" 
                        "in the past tense. It's driving me crazy!"), 
                        author=self.user, group=self.group
            ) 
                 

    def test_profile(self):
        # формируем GET-запрос к странице сайта
        response = self.client.get("/sarah/")
        # проверяем что страница найдена
        self.assertEqual(response.status_code, 200)

    def test_new_login_user(self):
        self.client.force_login(self.user)
        response = self.client.get("/new/")
        self.assertEqual(response.status_code, 200)

    def test_new_nonlogin_user(self):
        response = self.client.get("/new/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=/new/")

    def test_new_post(self):
    # После публикации поста новая запись появляется на главной странице сайта (index), 
    # на персональной странице пользователя (profile), и на отдельной странице поста (post)
        url = reverse("new_post")
        login_client = self.client
        login_client.force_login(self.user)
        response = login_client.post(
            url,
            {"text": "test post", "group": self.group.id},
            follow=True
        )
        self.assertRedirects(response, reverse("index"))
        self.assertContains(response, "test post")
        response = self.client.get("/sarah/")
        self.assertContains(response, "test post") 
        response = self.client.get("/sarah/2/")
        self.assertContains(response, "test post")   

    def test_edit_post(self):
    # Авторизованный пользователь может отредактировать свой пост и его содержимое 
    # изменится на всех связанных страницах
        self.client.force_login(self.user)
        response = self.client.get("/sarah/1/edit/")
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/sarah/1/edit/", 
                                    {"text": "test post edit"}, 
                                    follow=True)
        self.assertRedirects(response, "/sarah/")
        self.assertContains(response, "test post edit")
        response = self.client.get(reverse("index"))
        self.assertContains(response, "test post edit") 
        response = self.client.get("/sarah/1/")
        self.assertContains(response, "test post edit")                            
