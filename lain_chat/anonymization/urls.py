from django.urls import path
from . import views

app_name = 'anonymization'

urlpatterns = [
    # Gestion des layers
    path('create/', views.CreateLayerView.as_view(), name='create_layer'),
    path('switch/<uuid:layer_id>/', views.SwitchLayerView.as_view(), name='switch_layer'),
    path('burn/<uuid:layer_id>/', views.BurnLayerView.as_view(), name='burn_layer'),
    path('fragment/', views.FragmentIdentityView.as_view(), name='fragment_identity'),
    
    # Modes spéciaux
    path('nobody/', views.NobodyModeView.as_view(), name='nobody_mode'),
    path('god-knows/', views.GodKnowsModeView.as_view(), name='god_knows_mode'),
    
    # Urgence
    path('emergency/burn/', views.EmergencyBurnView.as_view(), name='emergency_burn'),
    
    # API
    path('api/layers/', views.LayerListAPIView.as_view(), name='layer_api'),
    path('api/status/', views.AnonymizationStatusAPIView.as_view(), name='status_api'),
]
