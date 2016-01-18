from django.shortcuts import render
from crowdsourcing.models import Task, Project
from mturk.models import MTurkHIT
from crowdsourcing.utils import get_model_or_none


def create_hits(request, *args, **kwargs):
    from mturk.interface import MTurkProvider
    provider = MTurkProvider('https://localhost:8000')
    project = Project.objects.get(id=1)
    task = Task.objects.get(project_id=1)
    provider.create_hits(project=project, tasks=[task])
    return None


def get_task(request, *args, **kwargs):
    task_id = request.GET.get('task_id', -1)
    hit_id = request.GET.get('hitId', -1)
    worker_id = request.GET.get('workerId', -1)
    assignment_id = request.GET.get('assignmentId', -1)
    #mturk_hit = get_model_or_none(MTurkHIT, task_id=task_id, hit_id=hit_id)
    #if not mturk_hit:
    #    return render(request, 'notification/message.html', {'message': 'HIT mismatch'})

    return render(request, 'mturk_index.html')
