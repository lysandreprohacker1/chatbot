from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from chatterbot import ChatBot
from chatterbot.ext.django_chatterbot import settings

from .serializers import ChatbotSerializer


class ChatbotViewSet(GenericViewSet):

    serializer_class = ChatbotSerializer

    chatterbot = ChatBot(**settings.CHATTERBOT)

    def list(self, request, *args, **kwargs):
        return Response({
            'name': self.chatterbot.name
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = self.chatterbot.get_response(serializer.data)
        return Response(response.serialize(), status=200)