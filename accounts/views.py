from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from dashboard.models import ActivityLog
from analyzer.models import PasswordAnalysis
from vault.models import VaultEntry


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'accounts/register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken!')
            return render(request, 'accounts/register.html')
        if len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters!')
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        UserProfile.objects.create(user=user)
        login(request, user)
        ActivityLog.objects.create(user=user, action='login', description='Account created & logged in')
        messages.success(request, f'Welcome to PassGuard Pro, {username}!')
        return redirect('dashboard')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            ActivityLog.objects.create(user=user, action='login', description='Logged in successfully')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password!')

    return render(request, 'accounts/login.html')


def logout_view(request):
    if request.user.is_authenticated:
        ActivityLog.objects.create(user=request.user, action='logout', description='Logged out')
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Stats
    total_analyzed = PasswordAnalysis.objects.filter(user=user).count()
    total_vault = VaultEntry.objects.filter(user=user).count()
    total_breached = PasswordAnalysis.objects.filter(user=user, was_breached=True).count()
    recent_logs = ActivityLog.objects.filter(user=user).order_by('-created_at')[:5]

    if request.method == 'POST':
        action = request.POST.get('action')

        # Update profile info
        if action == 'update_info':
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()

            if email and User.objects.filter(email=email).exclude(pk=user.pk).exists():
                messages.error(request, 'Email already in use!')
            else:
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                messages.success(request, '✅ Profile updated successfully!')

        # Change password
        elif action == 'change_password':
            current_password = request.POST.get('current_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')

            if not user.check_password(current_password):
                messages.error(request, '❌ Current password is incorrect!')
            elif new_password1 != new_password2:
                messages.error(request, '❌ New passwords do not match!')
            elif len(new_password1) < 6:
                messages.error(request, '❌ Password must be at least 6 characters!')
            else:
                user.set_password(new_password1)
                user.save()
                update_session_auth_hash(request, user)
                ActivityLog.objects.create(
                    user=user,
                    action='login',
                    description='Password changed successfully'
                )
                messages.success(request, '✅ Password changed successfully!')

        return redirect('profile')

    context = {
        'profile': profile,
        'total_analyzed': total_analyzed,
        'total_vault': total_vault,
        'total_breached': total_breached,
        'recent_logs': recent_logs,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.user
        if user.check_password(password):
            user.delete()
            messages.success(request, 'Account deleted successfully.')
            return redirect('login')
        else:
            messages.error(request, '❌ Incorrect password!')
            return redirect('profile')
    return redirect('profile')