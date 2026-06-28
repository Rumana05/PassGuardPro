from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def vault_view(request):
    return render(request, 'vault/vault.html')