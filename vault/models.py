from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class VaultEntry(models.Model):
    CATEGORY_CHOICES = [
        ('social', 'Social Media'),
        ('banking', 'Banking'),
        ('work', 'Work'),
        ('email', 'Email'),
        ('shopping', 'Shopping'),
        ('gaming', 'Gaming'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    website_name = models.CharField(max_length=100)
    website_url = models.CharField(max_length=200, blank=True)
    username = models.CharField(max_length=100)
    encrypted_password = models.BinaryField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    notes = models.TextField(blank=True)
    is_favourite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.website_name} — {self.user.username}"

    class Meta:
        ordering = ['-created_at']
