from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def mturk_index(request, *args, **kwargs):
    from mturk.interface import MTurkProvider
    m = MTurkProvider('https://localhost:8000')
    from crowdsourcing.models import Project
    p = Project.objects.get(id=19)
    m.create_hits(p)
    return render(request, 'mturk_index.html')
