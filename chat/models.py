from django.db import models
from base.models import BaseModelWithUUID, User
from user_profile.models import Student, Parent, Teacher


class ChatSession(BaseModelWithUUID):
    room_name = models.CharField(max_length=255)
    person = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_sessions_student')
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='chat_sessions_teacher')


class ChatMessage(BaseModelWithUUID):
    chat_session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}: {self.message}"
