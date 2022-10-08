from django.urls import path
from .views import *

#from mainapp import views
from mainapp.apps import MainappConfig

app_name = MainappConfig.name

urlpatterns = [
    path('', MainPageView.as_view()),
    path('news/', NewsPageView.as_view()),
    path('courses/', CoursesPageView.as_view()),
    path('contacts/', ContactsPageView.as_view()),
    path('doc_site/', DocSitePageView.as_view()),
    path('login/', LoginPageView.as_view()),
]
