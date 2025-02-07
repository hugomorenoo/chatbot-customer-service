from django.urls import path
from .views import ask_question
from . import views

urlpatterns = [
    path("ask/", ask_question, name="ask_question"),
    path('', views.index, name='home')
]
