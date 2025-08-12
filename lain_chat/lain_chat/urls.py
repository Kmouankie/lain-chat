from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'LAIN CHAT SYSTEM',
            'subtitle': 'Present day, present time...',
            'available_modules': [
                {'name': 'Chat', 'url': '/chat/', 'description': 'Anonymous chat rooms'},
                {'name': 'Layer Management', 'url': '/layer/', 'description': 'Manage anonymous layers'},
                {'name': 'Wired', 'url': '/wired/', 'description': 'Advanced Lain features'},
                {'name': 'Auth', 'url': '/auth/', 'description': 'User authentication'},
            ]
        })
        return context

urlpatterns = [

    path('admin/', admin.site.urls),
    

    path('', HomeView.as_view(), name='home'),
    
   
    path('chat/', include('chat.urls', namespace='chat')),
    path('auth/', include('users.urls', namespace='users')),
    path('layer/', include('anonymization.urls', namespace='anonymization')),
    path('wired/', include('wired.urls', namespace='wired')),
    path('auth/', include('authentication.urls')),
]


if settings.DEBUG:
    
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "Lain Chat Administration"
admin.site.site_title = "Lain Chat Admin"
admin.site.index_title = "Present Day, Present Time"