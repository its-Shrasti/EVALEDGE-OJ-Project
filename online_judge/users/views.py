from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RegisterForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from problems.models import Submission

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('problem_list')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('problem_list')
    return render(request, 'login.html', {'form': form})


def home_view(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    return render(request, 'landing.html')



@login_required
def profile_view(request):
    user = request.user
    submissions = Submission.objects.filter(user=user).select_related('problem').order_by('-submitted_at')
    return render(request, 'profile.html', {
        'user': user,
        'submissions': submissions,
    })

# Create your views here.
