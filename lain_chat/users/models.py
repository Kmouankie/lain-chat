import uuid
import hashlib
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class MinimalUser(AbstractUser):
    """User model minimal - juste pour l'authentification"""
    #  seulement les champs essentiels
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    
    
    # Hash pour liaison avec layers (change à chaque session)
    session_hash = models.CharField(max_length=64, null=True, blank=True)
    
    # Statistiques anonymes (pas d'identification possible)
    layers_created_count = models.IntegerField(default=0)
    emergency_burns_used = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'minimal_users'
        verbose_name = 'Minimal User'
        verbose_name_plural = 'Minimal Users'
    
    def generate_session_hash(self):
        """Génère un hash unique pour cette session"""
        data = f"{self.id}:{timezone.now().timestamp()}"
        self.session_hash = hashlib.sha256(data.encode()).hexdigest()
        self.save()
        return self.session_hash
    
    def clear_session_hash(self):
        """Efface le hash de session (déconnexion)"""
        self.session_hash = None
        self.save()
    
    def increment_layer_count(self):
        """Incrémente le compteur de layers"""
        self.layers_created_count += 1
        self.save()
    
    def __str__(self):
        return f"User {self.username} (ID: {self.id})"