import logging
from typing import Dict, Union

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task
def send_feedback_mail(message_form: Dict[str, Union[int, str]]) -> None:
    logger.info(f"Sent message: '{message_form}'")
    model_user = get_user_model()
    user_obj = model_user.objects.get(pk=message_form["user_id"])
    send_mail(      #Функция отправки письма
        "TechSupport Help",  # subject (title)
        message_form["message"],  # message
        user_obj.email,  # send to
        #"kundasl1@gmail.com",
        ["kundasl1@gmail.com"],  # send from, list
        fail_silently=False,
    )
    return None
