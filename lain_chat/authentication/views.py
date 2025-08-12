import time
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View
import json
import hashlib
import secrets
import random

# Générateur de noms anonymes 
LAIN_NAMES = [
    'Layer01', 'Layer02', 'Layer03', 'Layer04', 'Layer05',
    'Phantom', 'Spectral', 'Digital', 'Wired', 'Protocol',
    'Cipher', 'Neural', 'Circuit', 'Matrix', 'Signal',
    'Ghost', 'Echo', 'Void', 'Nexus', 'Node',
    'Anon', 'User', 'Entity', 'Process', 'Thread'
]

def generate_lain_username():
    base = random.choice(LAIN_NAMES)
    suffix = random.randint(100, 999)
    return f"{base}{suffix}"

def generate_anonymous_hash(email):
    
    salt = "lain_wired_connection_2024"
    return hashlib.sha256(f"{email}{salt}".encode()).hexdigest()[:12]

class LainLoginView(View):
    
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('chat:index')
        return render(request, 'auth/login.html')
    
    def post(self, request):
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me', False)
        
        if not email or not password:
            messages.error(request, 'Email and password are required')
            return render(request, 'auth/login.html')
        
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Invalid credentials')
            return render(request, 'auth/login.html')
        
    
        user = authenticate(request, username=user.username, password=password)
        if user:
            login(request, user)
            
            
            if not remember_me:
                request.session.set_expiry(0)  
            
            
            next_url = request.GET.get('next', 'chat:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'auth/login.html')

class LainRegisterView(View):
    """Vue d'inscription Lain-style"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('chat:index')
        return render(request, 'auth/register.html')
    
    def post(self, request):
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        preferred_name = request.POST.get('preferred_name', '').strip()
        
    # Validations
        if not email or not password:
            messages.error(request, 'Email and password are required')
            return render(request, 'auth/register.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'auth/register.html')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return render(request, 'auth/register.html')
        
       
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'auth/register.html')
        
        
        if preferred_name:
            
            preferred_name = ''.join(c for c in preferred_name if c.isalnum())[:20]
            if len(preferred_name) < 3:
                preferred_name = ''
        
        if not preferred_name:
            preferred_name = generate_lain_username()
        
        
        username = preferred_name
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{preferred_name}{counter}"
            counter += 1
        
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=generate_anonymous_hash(email)  
            )
            
            
            login(request, user)
            
            messages.success(request, f'Welcome to the Wired, {username}!')
            return redirect('chat:index')
            
        except Exception as e:
            messages.error(request, 'Registration failed. Please try again.')
            return render(request, 'auth/register.html')

class LainLogoutView(View):
    
    
    def post(self, request):
        logout(request)
        messages.success(request, 'Disconnected from the Wired')
        return redirect('auth:login')

@login_required
def profile_view(request):
    
    return render(request, 'auth/profile.html', {
        'user': request.user,
        'anonymous_hash': request.user.first_name
    })

@method_decorator(csrf_exempt, name='dispatch')
class QuickConnectView(View):
    
    
    def post(self, request):
        data = json.loads(request.body)
        session_name = data.get('session_name', '').strip()
        
        if not session_name:
            session_name = generate_lain_username()
        
        # Crée une session anonyme
        request.session['anonymous_user'] = {
            'name': session_name,
            'hash': hashlib.sha256(f"{session_name}{secrets.token_hex(8)}".encode()).hexdigest()[:8],
            'created_at': time.time()
        }
        
        return JsonResponse({
            'success': True,
            'username': session_name,
            'anonymous_hash': request.session['anonymous_user']['hash']
        })


def lain_auth_required(view_func):
    
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        
       
        if 'anonymous_user' in request.session:
            return view_func(request, *args, **kwargs)
        
       
        return redirect('auth:login')
    
    return wrapper

def get_user_display_name(request):
    
    if request.user.is_authenticated:
        return request.user.username
    
    if 'anonymous_user' in request.session:
        return request.session['anonymous_user']['name']
    
    return 'anonymous'

def get_user_hash(request):
    
    if request.user.is_authenticated:
        return request.user.first_name or 'registered'
    
    if 'anonymous_user' in request.session:
        return request.session['anonymous_user']['hash']
    
    return 'unknown'