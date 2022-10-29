from django.urls import path

from authapp.views import * #change
from authapp import views #new
from authapp.apps import AuthappConfig

app_name = AuthappConfig.name # создаем вместе с namespace

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path(
        "profile_edit/<int:pk>/",
        views.ProfileEditView.as_view(), name="profile_edit",
    ),  # error403
]
