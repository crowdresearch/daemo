from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from crowdsourcing.models import Conversation, Message
from crowdsourcing.serializers.message import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = ConversationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(sender=request.user)
            return Response({'status': 'Conversation created'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


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
