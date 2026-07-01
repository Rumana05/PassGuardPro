from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from dashboard.models import ActivityLog

from .models import VaultEntry
from .encryption import encrypt_password, decrypt_password


@login_required
def vault_view(request):
    category = request.GET.get('category', '')
    entries = VaultEntry.objects.filter(user=request.user)
    if category:
        entries = entries.filter(category=category)

    # Decrypt passwords for display
    vault_data = []
    for entry in entries:
        vault_data.append({
            'id': entry.id,
            'website_name': entry.website_name,
            'website_url': entry.website_url,
            'username': entry.username,
            'password': decrypt_password(bytes(entry.encrypted_password).decode()),
            'category': entry.category,
            'category_display': entry.get_category_display(),
            'notes': entry.notes,
            'is_favourite': entry.is_favourite,
            'created_at': entry.created_at,
        })

    categories = VaultEntry.CATEGORY_CHOICES
    total = VaultEntry.objects.filter(user=request.user).count()

    return render(request, 'vault/vault.html', {
        'vault_data': vault_data,
        'categories': categories,
        'selected_category': category,
        'total': total,
    })


@login_required
def add_entry(request):
    if request.method == 'POST':
        website_name = request.POST.get('website_name')
        website_url = request.POST.get('website_url', '')
        username = request.POST.get('username')
        password = request.POST.get('password')
        category = request.POST.get('category', 'other')
        notes = request.POST.get('notes', '')

        encrypted = encrypt_password(password)
        VaultEntry.objects.create(
            user=request.user,
            website_name=website_name,
            website_url=website_url,
            username=username,
            encrypted_password=encrypted.encode(),
            category=category,
            notes=notes,
        )

        ActivityLog.objects.create(
            user=request.user,
            action='vault_add',
            description=f"Added '{website_name}' to vault"
        )


        messages.success(request, f'✅ {website_name} added to vault!')
        return redirect('vault')

    return redirect('vault')


@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(VaultEntry, id=entry_id, user=request.user)
    name = entry.website_name
    entry.delete()
    ActivityLog.objects.create(
        user=request.user,
        action='vault_delete',
        description=f"Deleted '{name}' from vault"
    )
    messages.success(request, f'🗑️ {name} deleted from vault!')
    return redirect('vault')

@login_required
def toggle_favourite(request, entry_id):
    entry = get_object_or_404(VaultEntry, id=entry_id, user=request.user)
    entry.is_favourite = not entry.is_favourite
    entry.save()
    return JsonResponse({'is_favourite': entry.is_favourite})


@login_required
def get_password(request, entry_id):
    entry = get_object_or_404(VaultEntry, id=entry_id, user=request.user)
    decrypted = decrypt_password(bytes(entry.encrypted_password).decode())
    return JsonResponse({'password': decrypted})