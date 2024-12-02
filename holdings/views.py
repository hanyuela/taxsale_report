from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def holdings(request):
    return render(request, 'holdings.html')