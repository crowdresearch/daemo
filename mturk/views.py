from django.shortcuts import render


def mturk_index(request, *args, **kwargs):
    from mturk.interface import MTurkProvider
    from crowdsourcing.models import Project, Task
    provider = MTurkProvider('https://localhost:8000')
    project = Project.objects.get(id=1)
    task = Task.objects.get(project_id=1)
    provider.create_hits(project=project, tasks=[task])
    return render(request, 'mturk_index.html')
