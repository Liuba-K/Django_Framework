from django.urls import path
from .views import *


from mainapp.apps import MainappConfig

app_name = MainappConfig.name # создаем вместе с namespace

urlpatterns = [
    path('', MainPageView.as_view(), name='main'),
    path('news/', NewsPageView.as_view(), name='news'),
    path('news/<int:page>/', NewsWithPaginatorView.as_view(), name='news_paginator'), #add обработка
    path('courses_list/', CoursesPageView.as_view(), name='courses'),
    path('contacts/', ContactsPageView.as_view(), name='contacts'),
    path('doc_site/', DocSitePageView.as_view(), name='docs'),

]
