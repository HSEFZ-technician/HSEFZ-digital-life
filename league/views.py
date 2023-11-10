from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.

# @login_required()
def index(request):
    return render(request, 'league/home.html')

def match_map(request):
    return render(request, 'league/match_map.html', {'title': 'EFZ体育联赛·赛程图'})