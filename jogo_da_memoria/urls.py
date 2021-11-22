from django.urls import path
from .views import JogoAPIView

urlpatterns = [
    path('', JogoAPIView.as_view()),
]
