from django.shortcuts import render

def checkin(request):
    return render(request, 'scheckin/legacy/checkin.html')