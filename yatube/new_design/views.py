from django.shortcuts import render

# Create your views here.

def index_new(request):
    return render(request,'index_new.html')