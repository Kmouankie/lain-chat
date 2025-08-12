import uuid
from django.db import models
from django.utils import timezone

class Room(models.Model):
    """Salles de chat"""
    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    layer_level = models.IntegerField(default=1) 
    is_wired_only = models.BooleanField(default=False)
    requires_fragmentation = models.BooleanField(default=False)
    anonymous_mode_only = models.BooleanField(default=False)  
    
    # Auto-destruction des messages
    auto_destroy_messages_hours = models.IntegerField(default=24)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'chat_rooms'
        verbose_name = 'Chat Room'
        verbose_name_plural = 'Chat Rooms'
    
    def __str__(self):
        return f"#{self.name} (Layer {self.layer_level})"
    
    def get_active_layers_count(self):
        from anonymization.models import AnonymousMessage
        return AnonymousMessage.objects.filter(
            room_name=self.name,
            timestamp__gte=timezone.now() - timezone.timedelta(minutes=10)
        ).values('layer_id').distinct().count()

class RoomHistory(models.Model):
    """Historique anonymisé des rooms"""
    history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_name = models.CharField(max_length=50)
    event_type = models.CharField(max_length=50) 
    timestamp = models.DateTimeField(auto_now_add=True)
    layer_count_at_time = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'room_history'
