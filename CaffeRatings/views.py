from django.shortcuts import render
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast
from .models import Cafe

# Create your views here.
def index(request):
    data = Cafe.objects.all().annotate(average_rating=Cast(Avg('rating__rating'), IntegerField()))
    context = {
        'logged': True,
        'data': data
    }
    return render(request=request, template_name='CaffeRatings/index.html', context=context)