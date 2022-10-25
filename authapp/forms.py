from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField


class CustomUserCreationForm(UserCreationForm):
    #можно создать field_order
    class Meta:
        model = get_user_model() #лучше использовать get_user_model
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "age",
            "avatar",
        )
        field_classes = {"username": UsernameField}