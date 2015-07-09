__author__ = 'dmorina'
from crowdsourcing import models
from datetime import datetime
from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from crowdsourcing.serializers.dynamic import DynamicFieldsModelSerializer
from rest_framework.exceptions import ValidationError
from crowdsourcing.models import Conversation, Message, MessageRecipient, UserMessage

class ConversationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.Conversation

    def create(self, **kwargs):
        Conversation.objects.get_or_create(sent_from=kwargs['sent_from'], **self.validated_data)
