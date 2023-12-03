from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404, FileResponse, HttpResponse
from .core import *
# Create your views here.


@login_required()
def index(request):
  if (not request.user.is_superuser):
    raise Http404
  if (request.GET.get("n") == None):
    return render(request, "bingo/index.html")
  s = ""
  s = gen(int(request.GET.get("n")))
  print(s)
  R = FileResponse(open(s, "rb"))
  return R