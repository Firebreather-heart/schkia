from django.template.response import TemplateResponse
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



def page_not_found(request, exception):
    return render(request, '404.html', status=404)


def server_error(request):
    return render(request, '500.html', status=500)


def bad_request(request, exception):
    return render(request, '400.html', status=400)


def custom_csrf_failure_view(request, reason=""):
    """
    A custom view for handling CSRF errors.
    """
    context = {"reason": reason}
    return TemplateResponse(request, "csrf_error.html", context, status=403)
