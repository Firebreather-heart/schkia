from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .models import Parent




def parent_login_view(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST['password']
        next_url = request.POST.get('next', '/')
        print(next_url, 'next')
        try:
            uname = Parent.objects.get(phone_number=phone).user.username
        except:
            return render(request, 'users/parent_login.html', {'error': 'Invalid Phone Number'})
        else:
            user = authenticate(request, username=uname, password=password)
            if user is not None:
                login(request, user)
                return redirect(next_url)
    next_url = request.GET.get('next', '/')
    print(next_url, 'next')
    return render(request, 'users/parent_login.html', {'next': next_url, 'error':''})


def parent_logout_view(request):
    logout(request)
    return redirect('parent_login')

