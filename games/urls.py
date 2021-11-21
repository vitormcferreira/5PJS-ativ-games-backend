from django.urls import include, path

urlpatterns = [
    path('jogo_da_memoria/', include('jogo_da_memoria.urls')),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
