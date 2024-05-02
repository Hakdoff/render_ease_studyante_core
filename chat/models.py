from django.db import models
from base.models import BaseModelWithUUID, User


class ChatSession(BaseModelWithUUID):
    room_name = models.CharField(max_length=255)
    person = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chat_sessions_student')
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chat_sessions_teacher')

    class Meta:
        ordering = ["-updated_at"]


class ChatMessage(BaseModelWithUUID):
    chat_session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}: {self.message}"
