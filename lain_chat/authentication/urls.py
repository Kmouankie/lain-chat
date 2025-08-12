from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.LainLoginView.as_view(), name='login'),
    path('register/', views.LainRegisterView.as_view(), name='register'),
    path('logout/', views.LainLogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('quick-connect/', views.QuickConnectView.as_view(), name='quick_connect'),
]