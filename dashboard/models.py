from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('analyze', 'Password Analyzed'),
        ('vault_add', 'Password Added to Vault'),
        ('vault_delete', 'Password Deleted from Vault'),
        ('generate', 'Password Generated'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.action} — {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']