from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render


@login_required
def dashboard_view(request: HttpRequest):
    return render(request, "dashboard/dashboard.html")
