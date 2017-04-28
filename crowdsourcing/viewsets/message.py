import ast
import json

from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets, mixins, serializers
from rest_framework.decorators import list_route, detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

from crowdsourcing import models
from crowdsourcing.exceptions import daemo_error
from crowdsourcing.models import Conversation, Message, ConversationRecipient
from crowdsourcing.redis import RedisProvider
from crowdsourcing.serializers.message import ConversationSerializer, MessageSerializer, RedisMessageSerializer, \
    ConversationRecipientSerializer
from crowdsourcing.utils import get_relative_time


class ConversationViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                          mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # check if conversation already exists
        recipients = request.data.get('recipients', False)

        if recipients:
            conversations = self.queryset.active().filter(
                Q(sender__id=recipients[0]) | Q(sender__id=request.user.id),
                recipients__in=[recipients[0], request.user.id]
            )

            if len(conversations) > 0:
                response_data = ConversationSerializer(instance=conversations[0], context={'request': request}).data
                return Response(data=response_data)

        serializer = ConversationSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            obj = serializer.create(sender=request.user)
            response_data = ConversationSerializer(instance=obj, context={'request': request}).data
            return Response(data=response_data)
        else:
            raise serializers.ValidationError(detail=serializer.errors)

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.exclude(messages__isnull=True).active() \
            .filter(recipients__in=ConversationRecipient.objects.values_list('recipient', flat=True).active()
                    .filter(recipient=request.user))

        serializer = self.serializer_class(instance=queryset, many=True, context={"request": request})

        return Response(serializer.data)

    @list_route(methods=['get'], url_path='list-open')
    def list_open(self, request, *args, **kwargs):
        open_conversations = ConversationRecipient.objects.active().filter(
            recipient=request.user,
            status__in=[ConversationRecipient.STATUS_OPEN,
                        ConversationRecipient.STATUS_MINIMIZED]
        )

        instances = self.queryset.filter(conversations__in=open_conversations)

        serializer = self.serializer_class(instance=instances, many=True,
                                           context={'request': request})

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['put'])
    def status(self, request, *args, **kwargs):
        recipient_status = request.data.get('status')

        overlay = ConversationRecipient.objects.active().get(recipient=request.user,
                                                             conversation=self.get_object())
        if recipient_status is not None:
            overlay.status = recipient_status
            overlay.save()

        return Response({'status': 'Status updated'})


class ConversationRecipientViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ConversationRecipient.objects.all()
    serializer_class = ConversationRecipientSerializer
    permission_classes = [IsAuthenticated]

    @list_route(methods=['get'], url_path='list-open')
    def list_open(self, request, *args, **kwargs):
        instances = self.queryset.active().filter(recipient=request.user,
                                                  status__in=[ConversationRecipient.STATUS_OPEN,
                                                              ConversationRecipient.STATUS_MINIMIZED])

        serializer = self.serializer_class(instance=instances, many=True, fields=('id', 'status',
                                                                                  'conversation'),
                                           context={'request': request})

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            serializer.create(sender=request.user)

            return Response({'status': 'Message sent'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['get'], url_path='list-by-conversation')
    def list_by_conversation(self, request, *args, **kwargs):
        queryset = self.queryset.filter(conversation_id=request.query_params.get('conversation', -1)) \
            .order_by('created_at')

        # mark as read
        models.MessageRecipient.objects.filter(
            message__conversation__id=request.query_params.get('conversation', -1),
            status__lt=models.MessageRecipient.STATUS_READ,
            recipient=request.user
        ).update(status=models.MessageRecipient.STATUS_READ, read_at=timezone.now())

        serializer = self.serializer_class(instance=queryset, many=True,
                                           fields=('body', 'time_relative',
                                                   'is_self'), context={'request': request})

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class RedisMessageViewSet(viewsets.ViewSet):
    serializer_class = RedisMessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = RedisMessageSerializer(data=request.data)
        provider = RedisProvider()
        conversation_key = provider.build_key('conversation', request.data['conversation'])
        conversation_raw = provider.get_list(conversation_key)

        if len(conversation_raw):
            recipients = ast.literal_eval(conversation_raw[0])

            if request.user.username not in recipients or request.data['recipient'] not in recipients:
                raise serializers.ValidationError(detail=daemo_error("Invalid recipient for this thread"))
        else:
            raise serializers.ValidationError(detail=daemo_error("Invalid conversation"))

        if serializer.is_valid():
            redis_publisher = RedisPublisher(facility='notifications', users=[request.data['recipient']])

            message = RedisMessage(json.dumps({"body": request.data['message'],
                                               "time_relative": get_relative_time(timezone.now()),
                                               "conversation": request.data['conversation'],
                                               "sender": request.user.username}))

            redis_publisher.publish_message(message)

            message_data = {
                "conversation": request.data['conversation'],
                "body": request.data['message']
            }

            serializer = MessageSerializer(data=message_data, context={'request': request})

            if serializer.is_valid():
                obj = serializer.create(sender=request.user)
                response_data = MessageSerializer(instance=obj, context={"request": request}).data
                return Response(data=response_data, status=status.HTTP_201_CREATED)
            raise serializers.ValidationError(detail=serializer.errors)
        else:
            raise serializers.ValidationError(detail=serializer.errors)
