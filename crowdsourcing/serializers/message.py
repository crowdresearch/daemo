from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Q

from crowdsourcing import models
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from crowdsourcing.models import Conversation, Message, ConversationRecipient, UserMessage
from crowdsourcing.redis import RedisProvider
from crowdsourcing.utils import get_relative_time


class MessageSerializer(DynamicFieldsModelSerializer):
    time_relative = serializers.SerializerMethodField()
    is_self = serializers.SerializerMethodField()

    class Meta:
        model = models.Message
        fields = ('id', 'conversation', 'sender', 'created_timestamp', 'last_updated', 'body', 'status',
                  'time_relative', 'is_self')
        read_only_fields = ('created_timestamp', 'last_updated', 'sender')

    def create(self, **kwargs):
        message = Message.objects.create(sender=kwargs['sender'], **self.validated_data)
        for recipient in message.conversation.recipients.all():
            UserMessage.objects.get_or_create(user=recipient, message=message)
        return message

    def get_time_relative(self, obj):
        return get_relative_time(obj.created_timestamp)

    def get_is_self(self, obj):
        return obj.sender == self.context['request'].user


class ConversationSerializer(DynamicFieldsModelSerializer):
    recipient_names = serializers.SerializerMethodField()
    recipients = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    # messages = MessageSerializer(many=True, read_only=True)
    sender = serializers.StringRelatedField()
    is_sender_online = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = models.Conversation
        fields = ('id', 'subject', 'sender', 'created_timestamp', 'last_updated', 'recipients', 'last_message',
                  'recipient_names', 'is_sender_online')
        read_only_fields = ('created_timestamp', 'last_updated', 'sender', 'is_sender_online')

    def create(self, **kwargs):
        recipients = self.validated_data.pop('recipients')
        recipient_obj = ConversationRecipient.objects.filter(recipient__in=recipients,
                                                             conversation__sender=self.context.get('request').user)
        if recipient_obj.count() == len(recipients) and len(recipients) > 0:
            return recipient_obj.first().conversation

        conversation = Conversation.objects.create(sender=kwargs['sender'], **self.validated_data)
        usernames = []
        recipients.append(self.context['request'].user)
        for recipient in recipients:
            ConversationRecipient.objects.get_or_create(conversation=conversation, recipient=recipient)
            usernames.append(recipient.username)
        provider = RedisProvider()
        key = provider.build_key('conversation', conversation.id)
        if not provider.exists(key=key):
            provider.push(key=key, values=usernames)
        return conversation

    def get_recipient_names(self, obj):
        if obj is not None:
            return obj.recipients.values_list('username', flat=True).filter(
                ~Q(username=self.context.get('request').user))
        return []

    @staticmethod
    def get_last_message(obj):
        return MessageSerializer(instance=obj.messages.order_by('-created_timestamp').first(),
                                 fields=('body', 'created_timestamp', 'status', 'time_relative')).data

    def get_is_sender_online(self, obj):
        if obj and obj.sender:
            provider = RedisProvider()
            return provider.get_status('online', obj.sender.id) > 0
        return False


class CommentSerializer(DynamicFieldsModelSerializer):
    sender_alias = serializers.SerializerMethodField()
    posted_time = serializers.SerializerMethodField()

    class Meta:
        model = models.Comment
        fields = ('id', 'sender', 'body', 'parent', 'deleted', 'created_timestamp',
                  'last_updated', 'sender_alias', 'posted_time')
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


class RedisMessageSerializer(serializers.Serializer):
    recipient = serializers.CharField(max_length=64)
    message = serializers.CharField()


class ConversationRecipientSerializer(DynamicFieldsModelSerializer):
    conversation = serializers.SerializerMethodField()

    class Meta:
        model = models.ConversationRecipient
        fields = ('status', 'id', 'recipient', 'conversation',)

    def update(self, *args, **kwargs):
        self.instance.status = self.validated_data.get('status', self.instance.status)
        self.instance.save()
        return self.instance

    def get_conversation(self, obj):
        if obj is not None:
            return ConversationSerializer(instance=obj.conversation, context=self.context
                                          ).data
        return None
