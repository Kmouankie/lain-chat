from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    
    path('<str:room_name>/', views.room, name='room'),
    
    path('layer/create/', views.create_layer, name='create_layer'),
    path('layer/<str:room_name>/info/', views.layer_info, name='layer_info'),
    path('layer/<str:room_name>/status/', views.layer_status, name='layer_status'),
    path('layer/<str:room_name>/delete/', views.delete_layer, name='delete_layer'),
    
    # API endpoints
    path('api/rooms/', views.room_list, name='room_list'),
    path('api/quote/', views.random_lain_quote, name='random_quote'),
    
    # Gestion d'erreurs
    path('error/room/<str:room_name>/', views.room_not_found, name='room_not_found'),
]