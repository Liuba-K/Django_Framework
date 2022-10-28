from django.urls import path
from django.views.decorators.cache import cache_page

from .views import *

from mainapp.apps import MainappConfig

app_name = MainappConfig.name  # создаем вместе с namespace

urlpatterns = [
    path('', MainPageView.as_view(), name='main'),  #"main_page"
    #path("news/<int:pk>", NewsDetailView.as_view(), name="news_detail"),

    path("news/", NewsListView.as_view(), name="news"),
    path("news/create/", NewsCreateView.as_view(), name="news_create"),
    path("news/<int:pk>/detail", NewsDetailView.as_view(), name="news_detail"),
    path("news/<int:pk>/update", NewsUpdateView.as_view(), name="news_update"),
    path("news/<int:pk>/delete", NewsDeleteView.as_view(), name="news_delete"),

    path("courses/", cache_page(60 * 5)(CoursesListView.as_view()), name="courses"),# 5 minutes
    #path("courses/", CoursesListView.as_view(), name="courses"),
    path("courses/<int:pk>/", CoursesDetailView.as_view(), name="courses_detail"),
    path("course_feedback/", CourseFeedbackFormProcessView.as_view(), name="course_feedback"),
    #path('courses_list/', CoursesPageView.as_view(), name='courses'),
    path('contacts/', ContactsPageView.as_view(), name='contacts'),
    path('doc_site/', DocSitePageView.as_view(), name='docs'),  # "doc_site"
    path("log_view/", LogView.as_view(), name="log_view"),
    path("log_download/", LogDownloadView.as_view(), name="log_download"),

]
