from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from rest_framework.exceptions import ValidationError
from crowdsourcing.models import Conversation, Message, ConversationRecipient, UserMessage


class MessageSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = models.Message
        fields = ('id', 'conversation', 'sender', 'created_timestamp', 'last_updated', 'body', 'status')
        read_only_fields = ('created_timestamp', 'last_updated', 'sender')

    def create(self, **kwargs):
        message = Message.objects.get_or_create(sender=kwargs['sender'], **self.validated_data)
        for recipient in message[0].conversation.recipients.all():
            UserMessage.objects.get_or_create(user=recipient, message=message[0])


class ConversationSerializer(DynamicFieldsModelSerializer):
    recipients = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = models.Conversation
        fields = ('id', 'subject', 'sender', 'created_timestamp', 'last_updated', 'recipients', 'messages')
        read_only_fields = ('created_timestamp', 'last_updated', 'sender')

    def create(self, **kwargs):
        recipients = self.validated_data.pop('recipients')
        conversation = Conversation.objects.get_or_create(sender=kwargs['sender'], **self.validated_data)
        for recipient in recipients:
            ConversationRecipient.objects.get_or_create(conversation=conversation[0], recipient=recipient)


class CommentSerializer(DynamicFieldsModelSerializer):
    sender_alias = serializers.SerializerMethodField()
    posted_time = serializers.SerializerMethodField()

    class Meta:
        model = models.Comment
        fields = ('id', 'sender', 'body', 'parent', 'deleted', 'created_timestamp', 'last_updated', 'sender_alias', 'posted_time')
        read_only_fields = ('sender', 'sender_alias', 'posted_time')

    def get_sender_alias(self, obj):
        if hasattr(obj.sender, 'requester'):
            return obj.sender.requester.alias
        elif hasattr(obj.sender, 'worker'):
            return obj.sender.worker.alias
        else:
            return 'unknown'

    def get_posted_time(self, obj):
        from crowdsourcing.utils import get_time_delta
        delta = get_time_delta(obj.created_timestamp)
        return delta

    def create(self, **kwargs):
        comment = models.Comment.objects.create(sender=kwargs['sender'], deleted=False, **self.validated_data)
        return comment


