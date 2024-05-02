from rest_framework import serializers

from user_profile.serializers import UserSerializer
from .models import ChatSession, ChatMessage


class ChatMessageSerializers(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = ChatMessage
        fields = ('__all__')


class ChatSessionSerializers(serializers.ModelSerializer):
    person = UserSerializer()
    teacher = UserSerializer()
    
    class Meta:
        model = ChatSession
        fields = ('__all__')
    
    # def to_representation(self, instance):
    #     data = super(ChatSessionSerializers,
    #                  self).to_representation(instance)

    #     chat_session_id = data['id']
    #     chat_messages = ChatMessage.objects.filter(chat_session__pk=chat_session_id)

    #     data['chats'] = ChatMessageSerializers(chat_messages, many=True).data
    #     return data

