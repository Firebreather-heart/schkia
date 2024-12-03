from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    return render(request, 'dashboard/parent_dashboard.html')


def correspondences(request):
    return render(request, 'correspondences.html')


def e_learning(request):
    return render(request, 'e_learning.html')


def student_results(request):
    return render(request, 'student_results.html')


def bills(request):
    return render(request, 'bills.html')


def payment_histories(request):
    return render(request, 'payment_histories.html')


def change_password(request):
    return render(request, 'change_password.html')
