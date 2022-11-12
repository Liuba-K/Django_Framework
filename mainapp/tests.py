from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.mail import send_mail
from django.core import mail as django_mail
from django.urls import reverse
from selenium.webdriver.chrome.webdriver import WebDriver

from selenium.webdriver.support import expected_conditions as EC
from authapp import models as authapp_models
from selenium import webdriver
from pathlib import Path
import pickle #add
from http import HTTPStatus

from unittest import mock #add
from django.test import TestCase, Client
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from authapp.models import CustomUser
from config import settings
from mainapp.models import News, CourseFeedback, Courses

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
        self.assertEqual(result.status_code, HTTPStatus.OK)

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


class TestCoursesWithMock(TestCase):

# Тест, проверяющий доступность страницы, которая использует систему кеширования.
# ? cache feedback and course...через 5 мин
    def setUp(self) -> None:
        super().setUp()

        self.user = CustomUser.objects.create_superuser(username='admin', password='1')
        self.client_with_auth = Client()
        path_auth = reverse("authapp:login")

        self.client_with_auth.post(  # аутентификации нового клиента
            path_auth, data={"username": "admin", "password": "1"}
        )

        self.course = Courses.objects.create(
            name = "Python"
        )


    def test_page_open_detail(self):
        course_obj = CourseFeedback.objects.create(
            user=self.user,
            course=self.course
        )
        #course_obj = mainapp_models.CourseFeedback.objects.get(pk=1)
        path = reverse("mainapp:courses_detail", args=[course_obj.pk])
        file_path = Path(__file__).resolve().parent / "fixtures" / "006_feedback_list_2.bin"
        with open(file_path, "rb" #заменила
        ) as inpf, mock.patch("django.core.cache.cache.get") as mocked_cache:
            loaded_cache = pickle.load(inpf)
            mocked_cache.return_value = loaded_cache
            print(loaded_cache)
            result = self.client_with_auth.get(path)
            self.assertEqual(result.status_code, HTTPStatus.OK)
            self.assertTrue(mocked_cache.called)


class TestTaskMailSend(TestCase):
    def setUp(self) -> None:
        super().setUp()

        CustomUser.objects.create_superuser(username='admin', password='1')
        self.client_with_auth = Client()
        path_auth = reverse("authapp:login")
        self.client_with_auth.post(  # аутентификации нового клиента
            path_auth, data={"username": "admin", "password": "1"}
        )

    def test_mail_send(self):
        message_text = "test_message_text"
        user_obj = authapp_models.CustomUser.objects.first()
        mainapp_tasks.send_feedback_mail(
            {"user_id": user_obj.id, "message": message_text}
        )
        self.assertEqual(django_mail.outbox[0].body, message_text) # почему? django_mail
    #Для проверки отправки используется то, что по умолчанию в качестве бэкенда во время исполнения
#тестов используется django.core.mail.backends.locmem.EmailBackend. Он добавляет все отправленные
#сооб#щения в список outbox из модуля django.core.mail.


class TestNewsSelenium(StaticLiveServerTestCase):

    def setUp(self) -> None:
        super().setUp()

        for i in range(10):
            News.objects.create(
                title=f'Title{i}',
                preambule=f'Preamble{i}',
                body=f'Body{i}'
            )
        #CustomUser.objects.create_superuser(username='admin', password='1')
        #self.client_with_auth = Client()
        #path_auth = reverse("authapp:login")
        #self.client_with_auth.post(path_auth, data={"username": "admin", "password": "1"})

        #driver = webdriver.Chrome

        self.selenium = WebDriver(
            executable_path=settings.SELENIUM_DRIVER_PATH_FF/"chromedriver.exe"
        )
        self.selenium.implicitly_wait(10)
        # Login
        self.selenium.get(f"{self.live_server_url}{reverse('authapp:login')}")
        button_enter = WebDriverWait(self.selenium, 5).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '[type="submit"]')
            )
        )
        self.selenium.find_element("id", "id_username").send_keys("admin")
        self.selenium.find_element("id", "id_password").send_keys("1")
        button_enter.click()
        # Wait for footer
        WebDriverWait(self.selenium, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "toast-body")) #mt-auto
        )

    def test_create_button_clickable(self):
        path_list = f"{self.live_server_url}{reverse('mainapp:news')}"

        path_add = reverse("mainapp:news_create")

        self.selenium.get(path_list)
        button_create = WebDriverWait(self.selenium, 20).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, f'[href="{path_add}"]')
            )
        )
        print("Trying to click button ...")
        button_create.click()
        # Test that button clickable
        WebDriverWait(self.selenium, 20).until(
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
        navbar_el = WebDriverWait(self.selenium, 20).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "navbar"))
        )
        try:
            self.assertEqual(
                navbar_el.value_of_css_property("background-color"),
                "rgb(255, 255, 255, 1)",
            )
        except AssertionError:
            file_path = Path(__file__).resolve().parent.parent / "var" / "screenshots"  #/ "001_navbar_el_scrnsht.png"
            with open(
                file_path, "wb"
            ) as outf:
                outf.write(navbar_el.screenshot_as_png)
            raise

    def tearDown(self):

        # Close browser
        self.selenium.quit()
        super().tearDown()


