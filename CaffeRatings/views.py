from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib import messages
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast
from .models import Cafe, City
from .forms import RegistrationForm


def index(request):
    data = City.objects.all()
    context = {
        'data': data
    }
    return render(request=request, template_name='CaffeRatings/index.html', context=context)


# Create your views here.
def city_load(request, city):
    data = Cafe.objects.filter(city__name=city).annotate(average_rating=Cast(Avg('rating__rating'), IntegerField()))
    
    if not data.exists():
        raise Http404('No cafes found in this city.')

    context = {
        'data': data,
        'city': city,
    }
    return render(request=request, template_name='CaffeRatings/cafe_list.html', context=context)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if password1 == password2:
                user = form.save(commit=False)  # Create the user object but don't save it to the database yet
                user.set_password(password1)  # Set the password securely
                user.save()  # Now save the user to the database

                messages.success(request, f'Your account has been created, {user.username}! Proceed to log in.')
                return redirect('login')
            else:
                form.add_error('password2', 'Passwords do not match')  # Add an error message to the form
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})



# def login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.valid():
#             pass
#         else:
#             form = LoginForm(request.POST)
#     else:
#         form = LoginForm()
#     return render(request=request, template_name='registration/login.html', context={'form': form})
