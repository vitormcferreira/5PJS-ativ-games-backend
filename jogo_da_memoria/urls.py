from django.urls import path
from .views import JogoAPIView, RankingListAPIView

urlpatterns = [
    path('', JogoAPIView.as_view()),
    path('ranking/', RankingListAPIView.as_view()),
]
