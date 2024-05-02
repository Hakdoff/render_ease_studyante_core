from django.shortcuts import render, redirect
from rest_framework import generics, permissions, response, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from base.models import User
from chat.models import ChatSession, ChatMessage
from chat.serializers import ChatSessionSerializers, ChatMessageSerializers
from core.paginate import ExtraSmallResultsSetPagination
from user_profile.serializers import UserSerializer
from django.db.models import Q


def chatPage(request, *args, **kwargs):
    context = {}
    return render(request, "chat/chatPage.html", context)

class SearchChatUserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description='Query params for student search it will be based on first_name and last_name',
                type=openapi.TYPE_STRING
            )
        ],
        operation_id='list_students'
    )
    def get_queryset(self):
        q = self.request.GET.get('q', None)

        user = self.request.user
        # schedules = Schedule.objects.filter(
        #     teacher__user=user).values('section')

        # if schedules.exists():
        #     registered_students = []
        #     parents = []
        #     if student:
        #         registered_students = Registration.objects.filter(Q(section__pk__in=schedules) & Q(Q(student__user__first_name__icontains=student) | Q(student__user__last_name__icontains=student))).order_by('student__user__lastname').values('student__user')
        #     if parent:
        #         parents = Parent.objects.all().values('user')
        if q:
            return User.objects.filter(Q(Q(first_name__icontains=q) | Q(last_name__icontains=q))).order_by('last_name')

        return []


class ChatSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSessionSerializers
    queryset = ChatSession.objects.all()
    permission_classes = [permissions.IsAuthenticated,]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'is_person',
                openapi.IN_QUERY,
                description='Query params for student search it will be based on first_name and last_name',
                type=openapi.TYPE_STRING
            )
        ],
        operation_id='list_students'
    )
    def get_queryset(self):
        is_person = self.request.GET.get('is_person', None)
        
        if is_person:
            return ChatSession.objects.filter(person=self.request.user)
        return ChatSession.objects.filter(teacher=self.request.user)

    def post(self, request, *args, **kwargs):
        teacher_id = request.data.get('teacher_id', None)
        person_id = request.data.get('person_id', None)
        room_name = request.data.get('room_name', None)

        person = User.objects.get(pk=person_id)
        teacher = User.objects.get(pk=teacher_id)

        check_exists = ChatSession.objects.filter(person=person, teacher=teacher)
        chat_session = None
        serializer = None
        if check_exists.exists():
            chat_session = check_exists.first()
        else:
            chat_session = ChatSession.objects.create(person=person, teacher=teacher, room_name=room_name)
       
        serializer = ChatSessionSerializers(chat_session)
        
        return response.Response(serializer.data,
                        status=status.HTTP_201_CREATED if not check_exists.exists() else status.HTTP_200_OK)


class ChatMessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializers
    queryset = ChatMessage.objects.all()
    permission_classes = [permissions.IsAuthenticated,]
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        session_id = self.request.GET.get('session_id', None)

        if session_id:
            return ChatMessage.objects.filter(chat_session__pk=session_id)
        
        return []


class ChatMessageRetrieveView(generics.RetrieveAPIView):
    serializer_class = ChatSessionSerializers
    queryset = ChatSession.objects.all()
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        room_name = request.GET.get('room_name', None)

        chat_sessions = ChatSession.objects.filter(room_name=room_name)

        if chat_sessions.exists():
            serializer = ChatSessionSerializers(chat_sessions.first())
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        return response.Response({"error_message": "Not found"}, status=status.HTTP_400_BAD_REQUEST)
