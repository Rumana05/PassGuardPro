from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

from analyzer.models import PasswordAnalysis
from vault.models import VaultEntry
from .models import ActivityLog


@login_required
def dashboard_view(request):
    user = request.user

    # Stats
    total_analyzed = PasswordAnalysis.objects.filter(user=user).count()
    total_vault = VaultEntry.objects.filter(user=user).count()
    total_breached = PasswordAnalysis.objects.filter(user=user, was_breached=True).count()
    total_logs = ActivityLog.objects.filter(user=user).count()

    # Strength distribution
    very_strong = PasswordAnalysis.objects.filter(user=user, strength_label='Very Strong').count()
    strong = PasswordAnalysis.objects.filter(user=user, strength_label='Strong').count()
    moderate = PasswordAnalysis.objects.filter(user=user, strength_label='Moderate').count()
    weak = PasswordAnalysis.objects.filter(user=user, strength_label='Weak').count()
    very_weak = PasswordAnalysis.objects.filter(user=user, strength_label='Very Weak').count()

    # Security score (0-100)
    if total_vault > 0:
        strong_count = VaultEntry.objects.filter(user=user).count()
        security_score = min(100, int((very_strong + strong) / max(total_analyzed, 1) * 100))
    else:
        security_score = 0

    # Vault category distribution
    categories = {}
    for entry in VaultEntry.objects.filter(user=user):
        cat = entry.get_category_display()
        categories[cat] = categories.get(cat, 0) + 1

    # Recent activity
    recent_analysis = PasswordAnalysis.objects.filter(user=user).order_by('-checked_at')[:5]
    recent_logs = ActivityLog.objects.filter(user=user).order_by('-created_at')[:8]

    # Chart data
    strength_chart = {
        'labels': ['Very Strong', 'Strong', 'Moderate', 'Weak', 'Very Weak'],
        'data': [very_strong, strong, moderate, weak, very_weak],
        'colors': ['#16a34a', '#0ea5e9', '#ca8a04', '#ea580c', '#dc2626'],
    }

    category_chart = {
        'labels': list(categories.keys()),
        'data': list(categories.values()),
    }

    context = {
        'total_analyzed': total_analyzed,
        'total_vault': total_vault,
        'total_breached': total_breached,
        'total_logs': total_logs,
        'security_score': security_score,
        'strength_chart': json.dumps(strength_chart),
        'category_chart': json.dumps(category_chart),
        'recent_analysis': recent_analysis,
        'recent_logs': recent_logs,
        'very_strong': very_strong,
        'strong': strong,
        'moderate': moderate,
        'weak': weak,
        'very_weak': very_weak,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def generator_view(request):
    return render(request, 'dashboard/generator.html')


@login_required
def activity_log_view(request):
    logs = ActivityLog.objects.filter(user=request.user).order_by('-created_at')[:50]
    return render(request, 'dashboard/activity_log.html', {'logs': logs})