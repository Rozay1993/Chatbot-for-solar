# todo/todo_api/urls.py : API urls.py
from django.urls import path, include
from .views import (
    Chatbot,
)

urlpatterns = [
    path('chat', Chatbot.as_view()),
]