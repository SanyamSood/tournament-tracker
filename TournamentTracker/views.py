from django.shortcuts import render

def select_sport(request):
    return render(request, 'select_sport.html')