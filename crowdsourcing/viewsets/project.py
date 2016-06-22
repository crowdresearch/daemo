from django.db import connection

from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from crowdsourcing.models import Category, Project, Task
from crowdsourcing.permissions.project import IsProjectOwnerOrCollaborator, ProjectChangesAllowed
from crowdsourcing.serializers.project import *
from crowdsourcing.serializers.task import *
from crowdsourcing.tasks import create_tasks_for_project
from crowdsourcing.validators.project import validate_account_balance


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.active()
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectOwnerOrCollaborator, IsAuthenticated, ProjectChangesAllowed]

    def create(self, request, with_defaults=True, *args, **kwargs):
        serializer = ProjectSerializer(
            data=request.data,
            fields=('name', 'price', 'post_mturk', 'repetition', 'template'),
            context={'request': request}
        )

        if serializer.is_valid():
            with transaction.atomic():
                project = serializer.create(owner=request.user, with_defaults=with_defaults)

                serializer = ProjectSerializer(
                    instance=project,
                    fields=('id', 'name'),
                    context={'request': request}
                )

                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'], url_path='create-full')
    def create_full(self, request, *args, **kwargs):
        price = request.data.get('price')
        post_mturk = request.data.get('post_mturk', False)
        repetition = request.data.get('repetition', 1)
        if not post_mturk:
            validate_account_balance(request, price * repetition)
        return self.create(request=request, with_defaults=False, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        serializer = ProjectSerializer(instance=self.get_object(),
                                       fields=('id', 'name', 'price', 'repetition', 'deadline', 'timeout',
                                               'is_prototype', 'template', 'status', 'batch_files', 'post_mturk',
                                               'qualification', 'group_id', 'relaunch'),
                                       context={'request': request})

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectSerializer(
            instance=instance, data=request.data, partial=True, context={'request': request}
        )

        if serializer.is_valid():
            with transaction.atomic():
                serializer.update()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.hard_delete()
        return Response(data='', status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['PUT'])
    def update_status(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = request.data.get('status', instance.status)
        instance.save()
        return Response({}, status=status.HTTP_200_OK)

    @detail_route(methods=['POST'])
    def publish(self, request, *args, **kwargs):
        cursor = connection.cursor()
        # noinspection SqlResolve
        payment_query = '''
            SELECT sum(payment.pay) + sum(payment.additional_pay) total_payment
                FROM (
                       SELECT
                         t_previous.id id,
                         CASE WHEN coalesce(t_previous.include_next, FALSE) = FALSE
                           THEN coalesce(t_current.repetition, 0) * coalesce(t_current.price, 0) -
                                (coalesce(t_previous.repetition, 0) - coalesce(t_previous.in_progress, 0) -
                                 coalesce(t_previous.approved, 0)) *
                                coalesce(t_previous.price, 0)
                         ELSE
                           (coalesce(t_current.repetition, 0) - coalesce(t_previous.in_progress, 0)
                           - coalesce(t_previous.approved, 0))
                           *
                           coalesce(t_current.price) -
                           (t_previous.price * (t_previous.repetition - t_previous.in_progress - t_previous.approved))
                         END           pay,
                         CASE WHEN t_current.price IS NOT NULL AND t_previous.price IS NOT NULL AND
                                   coalesce(t_previous.include_next, FALSE) = TRUE
                                   AND t_current.price > t_previous.price
                           THEN (t_current.price - t_previous.price) * t_previous.in_progress
                         ELSE 0 END    additional_pay

                       FROM (
                              SELECT
                                t.id,
                                t.group_id,
                                t.include_next,
                                t.repetition,
                                t.price,
                                sum(t.approved)    approved,
                                sum(t.in_progress) in_progress
                              FROM (
                                     SELECT
                                       t.id,
                                       t.group_id,
                                       t.include_next,
                                       p.repetition,
                                       p.price,
                                       CASE WHEN tw.status = 3
                                         THEN
                                           1
                                       ELSE 0 END approved,
                                       CASE WHEN tw.status IN (1, 2, 5)
                                         THEN
                                           1
                                       ELSE 0 END in_progress
                                     FROM crowdsourcing_task t
                                       INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                                       LEFT OUTER JOIN crowdsourcing_taskworker tw ON tw.task_id = t.id
                                       AND tw.status NOT IN (4, 6, 7)
                                     WHERE project_id = (%(previous_pid)s)) t
                              GROUP BY t.id, t.group_id, t.include_next, t.repetition, t.price)
                            t_previous
                         FULL OUTER JOIN (SELECT
                                            t.id,
                                            t.group_id,
                                            p.repetition,
                                            p.price
                                          FROM crowdsourcing_task t
                                            INNER JOIN crowdsourcing_project p ON p.id = t.project_id
                                          WHERE project_id = (%(current_pid)s)) t_current
                           ON t_previous.group_id = t_current.group_id) payment;
        '''

        instance = self.get_object()
        previous_revision = models.Project.objects.filter(~Q(id=instance.id), group_id=instance.group_id) \
            .order_by('-id').first()
        previous_pid = previous_revision.id if previous_revision is not None else -1
        cursor.execute(payment_query, {'current_pid': instance.id, 'previous_pid': previous_pid})
        amount_due = cursor.fetchall()[0][0]

        serializer = ProjectSerializer(
            instance=instance, data=request.data, partial=True, context={'request': request}
        )
        if not instance.post_mturk:
            validate_account_balance(request, amount_due)

        if serializer.is_valid():
            with transaction.atomic():
                serializer.publish(amount_due)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['get'], url_path='for-workers')
    def worker_projects(self, request, *args, **kwargs):
        query = '''
            SELECT
              p.id,
              p.name,
              p.owner_id,
              p.status
            FROM crowdsourcing_taskworker tw
              INNER JOIN crowdsourcing_task t ON tw.task_id = t.id
              INNER JOIN crowdsourcing_project p ON p.id = t.project_id
            WHERE tw.status <> 6 AND tw.worker_id = (%(worker_id)s)
            GROUP BY p.id, p.name, p.owner_id, p.status
        '''
        projects = Project.objects.raw(query, params={'worker_id': request.user.id})

        serializer = ProjectSerializer(instance=projects, many=True,
                                       fields=('id', 'name', 'owner', 'status'),
                                       context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'], url_path='for-requesters')
    def requester_projects(self, request, *args, **kwargs):
        # noinspection SqlResolve
        query = '''
            SELECT
              p.id,
              name,
              created_at,
              updated_at,
              status,
              price,
              published_at
            FROM crowdsourcing_project p
              INNER JOIN (SELECT
                            group_id,
                            max(id) id
                          FROM crowdsourcing_project
                          GROUP BY group_id) p_max
                ON p.id = p_max.id
                WHERE owner_id=%(owner_id)s AND deleted_at IS NULL
                ORDER BY status, updated_at DESC
        '''
        projects = Project.objects.raw(query, params={'owner_id': request.user.id})
        serializer = ProjectSerializer(instance=projects, many=True,
                                       fields=('id', 'name', 'age', 'total_tasks', 'status', 'price'),
                                       context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['post'])
    def fork(self, request, *args, **kwargs):
        instance = self.get_object()
        project_serializer = ProjectSerializer(instance=instance, data=request.data, partial=True,
                                               fields=('id', 'name', 'price', 'repetition',
                                                       'is_prototype', 'template', 'status', 'batch_files'))
        if project_serializer.is_valid():
            with transaction.atomic():
                project_serializer.fork()
            return Response(data=project_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data=project_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'], permission_classes=[IsAuthenticated])
    def preview(self, request, *args, **kwargs):
        project = self.get_object()
        task = Task.objects.filter(project=project).first()
        task_serializer = TaskSerializer(instance=task, fields=('id', 'template'))
        return Response(data=task_serializer.data, status=status.HTTP_200_OK)

    @list_route(methods=['get'], url_path='task-feed')
    def task_feed(self, request, *args, **kwargs):
        projects = Project.objects.filter_by_boomerang(request.user)
        project_serializer = ProjectSerializer(instance=projects, many=True,
                                               fields=('id', 'name',
                                                       'timeout',
                                                       'available_tasks',
                                                       'price',
                                                       'task_time',
                                                       'owner',
                                                       'requester_rating', 'raw_rating', 'is_prototype',),
                                               context={'request': request})

        return Response(data=project_serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def comments(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectCommentSerializer(instance=instance.comments, many=True, fields=('comment', 'id',))
        response_data = {
            'project': kwargs['pk'],
            'comments': serializer.data
        }
        return Response(response_data, status.HTTP_200_OK)

    @detail_route(methods=['post'], url_path='post-comment')
    def post_comment(self, request, *args, **kwargs):
        serializer = ProjectCommentSerializer(data=request.data)
        comment_data = {}
        if serializer.is_valid():
            comment = serializer.create(project=kwargs['pk'], sender=request.user)
            comment_data = ProjectCommentSerializer(
                comment,
                fields=('id', 'comment',),
                context={'request': request}).data

        return Response(data=comment_data, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def attach_file(self, request, **kwargs):
        serializer = ProjectBatchFileSerializer(data=request.data, fields=('batch_file',))
        if serializer.is_valid():
            project_file = serializer.create(project=kwargs['pk'])
            file_serializer = ProjectBatchFileSerializer(instance=project_file)
            create_tasks_for_project.delay(kwargs['pk'], False)
            return Response(data=file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['delete'])
    def delete_file(self, request, **kwargs):
        batch_file = request.data.get('batch_file', None)
        instances = models.ProjectBatchFile.objects.filter(batch_file=batch_file)
        if instances.count() == 1:
            models.BatchFile.objects.filter(id=batch_file).delete()
        else:
            models.ProjectBatchFile.objects.filter(batch_file_id=batch_file, project_id=kwargs['pk']).delete()
        create_tasks_for_project.delay(kwargs['pk'], True)
        return Response(data={}, status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'], url_path='create-revision')
    def create_revision(self, request, *args, **kwargs):
        project = self.get_object()
        with transaction.atomic():
            revision = self.serializer_class.create_revision(instance=project)
        return Response(data={'id': revision.id}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], url_path='relaunch-info')
    def relaunch_info(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = self.serializer_class(instance=project, fields=('id', 'relaunch'))
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(deleted_at__isnull=True)
    serializer_class = CategorySerializer

    @detail_route(methods=['post'])
    def update_category(self, request):
        category_serializer = CategorySerializer(data=request.data)
        category = self.get_object()
        if category_serializer.is_valid():
            category_serializer.update(category, category_serializer.validated_data)

            return Response({'status': 'updated category'})
        else:
            return Response(category_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            category = self.queryset
            categories_serialized = CategorySerializer(category, many=True)
            return Response(categories_serialized.data)
        except:
            return Response([])

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        category.delete()
        return Response({'status': 'deleted category'})
