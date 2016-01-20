from django.shortcuts import render


def mturk_index(request, *args, **kwargs):
    return render(request, 'mturk_index.html')
