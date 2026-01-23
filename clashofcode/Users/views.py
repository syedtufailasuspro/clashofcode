from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


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
