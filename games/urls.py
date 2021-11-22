from django.urls import include, path

urlpatterns = [
    path('jogo_da_memoria/', include('jogo_da_memoria.urls')),
    path('accounts/', include('accounts.urls')),
]
