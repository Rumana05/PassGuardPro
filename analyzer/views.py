from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .utils import check_password_strength, check_breach, generate_password, mask_password
from .models import PasswordAnalysis


@login_required
def analyzer_view(request):
    recent = PasswordAnalysis.objects.filter(
        user=request.user
    ).order_by('-checked_at')[:5]
    return render(request, 'analyzer/analyzer.html', {'recent': recent})


@login_required
@csrf_exempt
def analyze_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        data = json.loads(request.body)
        password = data.get('password', '')
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not password:
        return JsonResponse({'error': 'Password required'}, status=400)

    result = check_password_strength(password)
    breached, breach_count = check_breach(password)

    # Save to DB
    PasswordAnalysis.objects.create(
        user=request.user,
        password_masked=mask_password(password),
        strength_label=result['strength'],
        strength_score=result['score'],
        entropy=result['details']['entropy'],
        was_breached=breached if breached is not None else False,
        breach_count=breach_count if breach_count else 0,
    )

    return JsonResponse({
        'strength': result['strength'],
        'strength_class': result['strength_class'],
        'score': result['score'],
        'bar_width': result['bar_width'],
        'feedback': result['feedback'],
        'details': result['details'],
        'breached': breached,
        'breach_count': breach_count,
        'suggestion': generate_password(),
    })
