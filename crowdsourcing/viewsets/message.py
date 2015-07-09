__author__ = 'dmorina'


from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from crowdsourcing.models import Conversation, Message
from crowdsourcing.serializers.message import ConversationSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes=[IsAuthenticated]

    def create(self, request, *args, **kwargs):
        module_serializer = ConversationSerializer(data=request.data)
        if module_serializer.is_valid():
            module_serializer.create(sent_from=request.user)
            return Response({'status': 'Conversation created'})
        else:
            return Response(module_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)