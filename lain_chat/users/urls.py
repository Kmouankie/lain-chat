from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentification minimale
    path('login/', views.MinimalLoginView.as_view(), name='login'),
    path('logout/', views.MinimalLogoutView.as_view(), name='logout'),
    path('register/', views.MinimalRegisterView.as_view(), name='register'),
    
    # Gestion session anonyme
    path('session/new/', views.AnonymousSessionView.as_view(), name='new_session'),
    path('session/destroy/', views.DestroySessionView.as_view(), name='destroy_session'),
]