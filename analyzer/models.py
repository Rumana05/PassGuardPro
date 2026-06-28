from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class PasswordAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password_masked = models.CharField(max_length=100)
    strength_label = models.CharField(max_length=20)
    strength_score = models.IntegerField()
    entropy = models.FloatField(default=0)
    was_breached = models.BooleanField(default=False)
    breach_count = models.IntegerField(default=0)
    checked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.strength_label} - {self.checked_at.strftime('%Y-%m-%d')}"
