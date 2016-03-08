from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def mturk_index(request, *args, **kwargs):
    return render(request, 'mturk/index.html')
