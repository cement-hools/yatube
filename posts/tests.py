from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from .models import Group, Post, User, Comment, Follow


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
        cache.clear()
    
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
            {"text": text, "group": self.group.id},
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
        response = self.client.post(
            reverse("new_post"),
            {"text": "text", "group": self.group.id},
            follow=True
        )
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
        """После публикации поста переходит на главную старницу сайта (index)"""
        post_text = "test post"
        response = self.add_new_post(post_text)
        self.assertRedirects(response, reverse("index"))
    
    def test_new_post_in_all_pages(self):
        """После публикации поста новая запись появляется на всех связанных страницах"""    
        post_text = "test post"
        url_list = [
            reverse("index"),
            reverse("profile", args=["sarah"]),
            reverse("post", args=[self.post.author.username, 2]),
            reverse("group", args=[self.group.slug]),
        ]
        self.add_new_post(post_text)        
        self.checking_text_in_pages(post_text, url_list)

    def test_edit_post_in_all_pages(self):
        """Проверка отредактированного текста на всех связанных страницах"""
        post_text = "test post edit"
        url_list = [
            reverse("index"),
            reverse("profile", args=["sarah"]),
            reverse("post", args=[self.post.author.username, self.post.id]),
            reverse("group", args=[self.group.slug]),
        ]
        self.edit_post(post_text)
        self.checking_text_in_pages(post_text, url_list)

    def test_404_page(self):
        """возвращает ли сервер код 404, если страница не найдена."""
        response = self.client.get("/404/")
        self.assertEqual(response.status_code, 404)
        
    def test_img_in_post_page(self):
        """проверяют страницу конкретной записи с картинкой: на странице есть тег <img>"""
        small_jpg = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        img = SimpleUploadedFile("small.gif", small_jpg,
                                 content_type="img/gif")
        text = "post with image"
        self.post = Post.objects.create(
            text=("You're talking about things I haven't done yet"
                  "in the past tense. It's driving me crazy!"),
            author=self.user,
            group=self.group,
            image=img,
        )
        response = self.client.get(reverse("post", 
                                           args=[self.user.username, 2]),)    
        self.assertContains(response, "<img")
        
    def test_img_in_all_page(self):
        """проверяют, что на главной странице, на странице профайла и на странице группы пост с картинкой отображается корректно, с тегом <img>"""
        small_jpg = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        img = SimpleUploadedFile("small.jpg", small_jpg, 
                                 content_type="media/posts")
        text = "post with image"
        response = self.login_client.post(
            reverse("new_post"),
            {
                "author": self.user, 
                "text": text, 
                "group": self.group.id, 
                "image": img}
            )   
        response = self.client.get(reverse("post", 
                                           args=[self.user.username, 2]),)    
        self.assertContains(response, "<img")
        url_list = [
            reverse("index"),
            reverse("profile", args=[self.user.username]),
            reverse("group", args=[self.group.slug]),
        ]
        self.checking_text_in_pages("<img", url_list)
        
    def test_img_file_upload_protection(self):
        """проверяют, что срабатывает защита от загрузки файлов не-графических форматов"""
        small_txt = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        img = SimpleUploadedFile("small.txt", small_txt, 
                                 content_type="media/posts")
        text = "post with image"
        response = self.login_client.post(
            reverse("new_post"),
            {
                "author": self.user, 
                "text": text, 
                "group": self.group.id, 
                "image": img}
            )   
        self.assertFormError(
            response, 
            form="form", 
            field="image", 
            errors=[
                ("Формат файлов 'txt' не поддерживается. "
                "Поддерживаемые форматы файлов: 'bmp, dib, gif, tif, tiff, "
                "jfif, jpe, jpg, jpeg, pbm, pgm, ppm, pnm, png, apng, blp, "
                "bufr, cur, pcx, dcx, dds, ps, eps, fit, fits, fli, flc, ftc, "
                "ftu, gbr, grib, h5, hdf, jp2, j2k, jpc, jpf, jpx, j2c, icns, "
                "ico, im, iim, mpg, mpeg, mpo, msp, palm, pcd, pdf, pxr, psd, "
                "bw, rgb, rgba, sgi, ras, tga, icb, vda, vst, webp, wmf, emf, "
                "xbm, xpm'.")
            ]
            )

    def test_login_user_can_follow(self):
        """Авторизованный пользователь может подписаться на автора"""
        author = User.objects.create_user(
            username="john", 
            email="connor.j@skynet.com", 
            password="12345"
        )
        response = self.login_client.get(
            reverse("profile_follow", args=[author.username]), 
            follow=True
            )
        self.assertContains(response, "Отписаться")  

    def test_login_user_can_unfollow(self):
        """Авторизованный пользователь может отподписаться на автора"""
        author = User.objects.create_user(
            username="john", 
            email="connor.j@skynet.com", 
            password="12345"
        )
        response = self.login_client.get(
            reverse("profile_follow", args=[author.username]), 
            follow=True
            )
        response = self.login_client.get(
            reverse("profile_unfollow", args=[author.username]), 
            follow=True
            )
        redirect = reverse("profile", args=[author.username])         
        self.assertContains(response, "Подписаться")
    
    def test_post_view_in_followed_user(self):
        """Новая запись пользователя появляется в ленте тех, кто на него подписан"""
        author = User.objects.create_user(
            username="john", 
            email="connor.j@skynet.com", 
            password="12345"
        )
        post = Post.objects.create(
            text=("FOLLOW"), 
            author=author, 
            group=self.group
        )
        response = self.login_client.get(
            reverse("profile_follow", args=[author.username]), 
            follow=True
            )
        response = self.login_client.get(reverse("follow_index"))
        self.assertContains(response, "FOLLOW")

    def test_post_not_view_in_not_followed_user(self):
        """Новая запись пользователя не появляется в ленте тех, кто на него не подписан"""
        author = User.objects.create_user(
            username="john", 
            email="connor.j@skynet.com", 
            password="12345"
        )
        post = Post.objects.create(
            text=("FOLLOW"), 
            author=author, 
            group=self.group
        )
        response = self.login_client.get(reverse("follow_index"))
        self.assertNotContains(response, "FOLLOW")

    def test_only_login_user_can_comment_post(self):
        """Только авторизированный пользователь может комментировать посты"""
        response = self.login_client.post(
            reverse("add_comment", args=[self.user.username, 1]),
            {"text": "My comment"},
            follow=True
        )
        response = self.client.get(reverse("post", 
                                           args=[self.user.username, 1]),)    
        self.assertContains(response, "My comment")
        
    def test_page(self):
        post_text = "test post"
        url_list = [
            reverse("index"),
            reverse("profile", args=["sarah"]),
            reverse("post", args=[self.post.author.username, 2]),
            reverse("group", args=[self.group.slug]),
        ]
        response = self.login_client.post(
            reverse("new_post"),
            {"text": post_text, "group": self.group.id},
            follow=True
        )
        response = self.client.get(reverse("index"))
        print(response)
        response = self.client.get(reverse("group", args=[self.group.slug]))
        print(response)
        for url in url_list:
            cache.clear()
            response = self.client.get(url)
            if response.context:
                if "page" in response.context:
                    print("page in context")
                    self.assertEqual(response.context["page"][0].group, 
                                     self.group)
                    self.assertEqual(response.context["page"][0].author, 
                                     self.user)
                    self.assertEqual(response.context["page"][0].text, 
                                     post_text)
                    self.assertContains(response, post_text)
                else:
                    print("page not in response")
                    self.assertEqual(response.context["post"].group, self.group)
                    self.assertEqual(response.context["post"].author, self.user)
                    self.assertEqual(response.context["post"].text, post_text)
                    self.assertContains(response, post_text)
            else:
                print("not context")                    
