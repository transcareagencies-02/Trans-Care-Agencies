from django.shortcuts import render


def faqs(request):
    return render(request, 'pages/faqs.html')


def terms(request):
    return render(request, 'pages/terms.html')

def privacy(request):
    return render(request, 'pages/privacy.html')

def warranty(request):
    return render(request, 'pages/warranty.html')