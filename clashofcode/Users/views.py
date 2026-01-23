from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.models import User

def login_user(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            return HttpResponse("WELCOME CHIEF")
            ...
        else:
            # Return an 'invalid login' error message.
            messages.success(request, ('ERROR'))
            return redirect('login')
    else:
        return render(request, 'authentication/login.html', {})




def signup_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken')
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'Account created successfully!')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')
    else:
        return render(request, 'authentication/signup.html', {})