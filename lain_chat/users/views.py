from django.shortcuts import render
from django.views.generic import TemplateView

class MinimalLoginView(TemplateView):
    template_name = 'auth/login.html'

class MinimalLogoutView(TemplateView):
    template_name = 'auth/logout.html'

class MinimalRegisterView(TemplateView):
    template_name = 'auth/register.html'

class AnonymousSessionView(TemplateView):
    template_name = 'auth/session.html'

class DestroySessionView(TemplateView):
    template_name = 'auth/destroy.html'