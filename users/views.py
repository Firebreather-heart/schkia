from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Parent




def parent_login_view(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST['password']
        try:
            uname = Parent.objects.get(phone_number=phone).user.username
        except:
            return render(request, 'users/parent_login.html', {'error': 'Invalid Phone Number'})
        else:
            user = authenticate(request, username=uname, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    return render(request, 'users/parent_login.html')


def parent_logout_view(request):
    logout(request)
    return redirect('parent_login')

