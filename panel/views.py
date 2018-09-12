from django.shortcuts import render

def panel(request):
    context = {
    }
    return render(request, 'panel/panel.html', context)
