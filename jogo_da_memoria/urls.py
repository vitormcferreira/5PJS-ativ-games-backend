from django.urls import path
from .views import Jogo

urlpatterns = [
    path('', Jogo.as_view()),
]
