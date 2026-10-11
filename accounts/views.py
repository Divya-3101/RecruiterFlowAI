from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth import authenticate,login,logout
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages



# Create your views here.

def register_view(request):
    if request.method=='POST':
        form= RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request,'accounts/register.html',{'form': form})



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        messages.error(request,'Invalid username or password.')
    return render(request,'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def home(request):
    return render(request,'accounts/home.html')


@login_required
def profile_view(request):
    if request.user.role != 'candidate':
        return redirect('home')
    profile, created = CandidateProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = CandidateProfileForm(request.POST,request.FILES,instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CandidateProfileForm(instance=profile)
    return render(request,'accounts/profile.html',{'form': form})

