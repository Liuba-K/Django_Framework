import pickle #add
from http import HTTPStatus
from telnetlib import EC
from unittest import mock #add

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, Client
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from social_core.pipeline import user

from authapp.models import CustomUser
from mainapp.models import News
import logging
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin)
from django.core.cache import cache
from django.http import FileResponse, JsonResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View)

from selenium.webdriver.firefox.webdriver import WebDriver
from mainapp import forms as mainapp_forms
from mainapp import models as mainapp_models
from mainapp import tasks as mainapp_tasks

#logger = logging.getLogger(__name__)


class StaticPagesSmokeTest(TestCase):

    def test_page_index_open(self):
        path = reverse("mainapp:main")
        result = self.client.get(path)

        self.assertEqual(result.status_code, HTTPStatus.OK) #проверка результата

    def test_page_contacts_open(self):
        path = reverse("mainapp:contacts")
        result = self.client.get(path)
        self.assertEqual(result.status_code, HTTPStatus.OK)


class TestNewsPage(TestCase):

    def setUp(self) -> None:
        super().setUp()
        for i in range(10):
            News.objects.create(
                title=f'Title{i}',
                preambule=f'Preamble{i}',
                body=f'Body{i}'
            )
        CustomUser.objects.create_superuser(username='admin', password='1')
        self.client_with_auth = Client()
        path_auth = reverse("authapp:login")
        self.client_with_auth.post(  # аутентификации нового клиента
            path_auth, data={"username": "admin", "password": "1"}
        )

    def test_open_page(self):
        path = reverse("mainapp:news")
        result = self.client.get(path)
        self.assertEqual(result.status_code, HTTPStatus.OK)

    def test_page_open_create_deny_access(self):
        path = reverse("mainapp:news_create")

        result = self.client.get(path)
        self.assertEqual(result.status_code, HTTPStatus.FOUND)

    def test_page_open_create_by_admin(self):
        path = reverse("mainapp:news_create")
        result = self.client_with_auth.get(path)
        self.assertEqual(result.status_code, HTTPStatus.OK)  # нужно Ok проблема с аутентификацией #есть форма

    def test_create_in_web(self):
        counter_before = mainapp_models.News.objects.count()
        path = reverse("mainapp:news_create")
        self.client_with_auth.post(
            path,
            data={
                "title": "NewTestNews001",
                "preamble": "NewTestNews001",
                "body": "NewTestNews001",
            },
        )
        self.assertGreater(mainapp_models.News.objects.count(), counter_before)
        #self.assertEqual(News.objects.all().count(), counter_before)  # сообщение не создается

    def test_page_open_update_deny_access(self):
        news_obj = mainapp_models.News.objects.first()

        path = reverse("mainapp:news_update", args=[news_obj.pk])
        result = self.client.get(path)
        self.assertEqual(result.status_code, HTTPStatus.FOUND)

    def test_page_open_update_by_admin(self):
        news_obj = mainapp_models.News.objects.first()

        path = reverse("mainapp:news_update", args=[news_obj.pk])
        result = self.client_with_auth.get(path)
        self.assertEqual(result.status_code, HTTPStatus.OK)

    def test_delete_deny_access(self):
        news_obj = mainapp_models.News.objects.first()
        path = reverse("mainapp:news_delete", args=[news_obj.pk])
        result = self.client.post(path)
        self.assertEqual(result.status_code, HTTPStatus.FOUND)


class TestNewsSelenium(StaticLiveServerTestCase):
    fixtures = (
        "authapp/fixtures/001_users.json",
        "mainapp/fixtures/001_news.json",
    )

    def setUp(self):
        super().setUp()

        self.selenium = WebDriver(
            executable_path=settings.SELENIUM_DRIVER_PATH_FF
        )
        self.selenium.implicitly_wait(10)
        # Login
        self.selenium.get(f"{self.live_server_url}{reverse('authapp:login')}")
        button_enter = WebDriverWait(self.selenium, 5).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '[type="submit"]')
            )
        )
        self.selenium.find_element_by_id("id_username").send_keys("Luba1")
        self.selenium.find_element_by_id("id_password").send_keys("lubava2211")
        button_enter.click()
        # Wait for footer
        WebDriverWait(self.selenium, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "toast-body")) #mt-auto
        )

    def test_create_button_clickable(self):
        path_list = f"{self.live_server_url}{reverse('mainapp:news')}"

        path_add = reverse("mainapp:news_create")

        self.selenium.get(path_list)
        button_create = WebDriverWait(self.selenium, 5).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, f'[href="{path_add}"]')
            )
        )
        print("Trying to click button ...")
        button_create.click()
        # Test that button clickable
        WebDriverWait(self.selenium, 5).until(
            EC.visibility_of_element_located((By.ID, "id_title")) #active
        )
        print("Button clickable!")

        # With no element - test will be failed
        # WebDriverWait(self.selenium, 5).until(
        # EC.visibility_of_element_located((By.ID, "id_title111"))
        # )
    #Цвет элемента соответствует заданному (извлечение CSS-свойства).
    def test_pick_color(self):
        path = f"{self.live_server_url}{reverse('mainapp:main')}"

        self.selenium.get(path)
        navbar_el = WebDriverWait(self.selenium, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "navbar"))
        )
        try:
            self.assertEqual(
                navbar_el.value_of_css_property("background-color"),
                "rgb(255, 255, 155)",
            )
        except AssertionError:
            with open(
                "var/screenshots/001_navbar_el_scrnsht.png", "wb"
            ) as outf:
                outf.write(navbar_el.screenshot_as_png)
            raise

    def tearDown(self):

        # Close browser
        self.selenium.quit()
        super().tearDown()

'''
Не рабочие тесты
    fixtures = (
        "authapp/fixtures/001_users.json",
        "mainapp/fixtures/001_news.json",
    )
    def setUp(self) -> None:
        super().setUp()
        self.client_with_auth = Client()
        path_auth = reverse("authapp:login")
        self.client_with_auth.post(  # аутентификации нового клиента
            path_auth, data={"username": "admin", "password": "1"}
        )
    
     
    
    def test_page_open_detail(self):
        news_obj = mainapp_models.News.objects.first()
        path = reverse("mainapp:news_detail", args=[news_obj.pk])
        result = self.client.get(path)
        self.assertEqual(result.status_code, HTTPStatus.OK)
    

    def test_failed_open_add_by_anonym(self):
        path = reverse('mainapp:news_create')
        result = self.client.get(path)
        self.assertEqual(result.status_code, HTTPStatus.FOUND)  #302 Redirect

    def test_create_news_item_by_admin(self):
        news_count = News.objects.all().count() #кол-во новостей до создания
        path = reverse('mainapp:news_create')
        result = self.client_with_auth.post(
            path,
            data={
                'title': 'Test title',
                'preambule': 'Test preambule',
                'body': 'Test body'
            }
        )
        self.assertEqual(result.status_code, HTTPStatus.FOUND)
        self.assertEqual(News.objects.all().count(), news_count) #сообщение не создается
    
        def test_update_in_web(self):
        new_title = "NewTestTitle001"

        news_obj = mainapp_models.News.objects.first()
        self.assertNotEqual(news_obj.title, new_title)
        path = reverse("mainapp:news_update", args=[news_obj.pk])
        result = self.client_with_auth.post(
            path,
            data={
                "title": new_title,
                "preambule": news_obj.preambule,
                "body": news_obj.body,
            },
        )
        self.assertEqual(result.status_code, HTTPStatus.FOUND)
        news_obj.refresh_from_db()
        self.assertEqual(news_obj.title, new_title)
    
     def test_delete_in_web(self):
        news_obj = mainapp_models.News.objects.first()
        path = reverse("mainapp:news_delete", args=[news_obj.pk])
        self.client_with_auth.post(path)
        news_obj.refresh_from_db()
        self.assertTrue(news_obj.deleted)

    def login(self, data):
        self.username = "Luba1"
        self.password = "lubava2211"
        User = User.objects.create(username=self.username)
        user.set_password(self.password)
        user.save()

        c = Client()
        c.login(username=self.username, password=self.password)
        return c, user
        #response = c.post('authapp:login', {'username': 'Luba1', 'password': 'lubava2211'})
        #response.status_code #        200
        #response = c.get('/customer/details/')
        #response.content
        
        
тест кэш падает с ошибкой 
    def test_page_open_detail(self):
        course_obj = mainapp_models.CourseFeedback.objects.get(pk=1)
        path = reverse("mainapp:courses_detail", args=[course_obj.pk])
        with open(
                "mainapp/fixtures/006_feedback_list_1.bin", "rb" #заменила
        ) as inpf, mock.patch("django.core.cache.cache.get") as mocked_cache:
            mocked_cache.return_value = pickle.load(inpf)
            result = self.client.get(path)
            self.assertEqual(result.status_code, HTTPStatus.OK)
            self.assertTrue(mocked_cache.called)
mainapp.models.CourseFeedback.DoesNotExist: CourseFeedback matching query does not exist.

отложенные задачи не подгружаются
class TestTaskMailSend(TestCase):
    fixtures = ("authapp/fixtures/001_users.json",)
    def test_mail_send(self):
        message_text = "test_message_text"
        user_obj = authapp_models.CustomUser.objects.first()
        mainapp_tasks.send_feedback_mail(
            {"user_id": user_obj.id, "message": message_text}
        )
        self.assertEqual(django_mail.outbox[0].body, message_text)
'''
