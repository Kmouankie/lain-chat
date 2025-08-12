from django.urls import path
from . import views

app_name = 'wired'

urlpatterns = [
    
    path('', views.WiredIndexView.as_view(), name='index'),
    path('present-day/', views.PresentDayView.as_view(), name='present_day'),
    path('present-time/', views.PresentTimeView.as_view(), name='present_time'),
    path('close-the-world/', views.CloseTheWorldView.as_view(), name='close_the_world'),
    path('open-the-next/', views.OpenTheNextView.as_view(), name='open_the_next'),
    
    # Easter eggs et réf
    path('cyberia/', views.CyberiaView.as_view(), name='cyberia'),
    path('knights/', views.KnightsView.as_view(), name='knights'),
    path('protocol-7/', views.Protocol7View.as_view(), name='protocol_7'),
]