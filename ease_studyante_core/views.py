import json
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from oauth2_provider.models import get_access_token_model
from oauth2_provider.signals import app_authorized
from oauth2_provider.views.base import TokenView
from dal import autocomplete
from django.db.models import Q

from base.models import User
from user_profile.models import Parent, Student, Teacher


class TokenViewWithUserId(TokenView):
    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        request_body = json.loads(request.body)

        username = request_body.get("username", None)
        is_parent = request_body.get("is_parent", None)
        is_student = request_body.get("is_student", None)
        is_teacher = request_body.get("is_teacher", None)

        if is_parent:
            if not Parent.objects.filter(user__username=username).exists():
                error_message = {
                    "error_description": "User not found"
                }
                return HttpResponse(content=json.dumps(error_message), status=404, content_type="application/json")

        if is_student:
            if not Student.objects.filter(user__username=username).exists():
                error_message = {
                    "error_description": "User not found"
                }
                return HttpResponse(content=json.dumps(error_message), status=404, content_type="application/json")

        if is_teacher:
            if not Teacher.objects.filter(user__username=username).exists():
                error_message = {
                    "error_description": "User not found"
                }
                return HttpResponse(content=json.dumps(error_message), status=404, content_type="application/json")

        if not is_teacher and not is_student and not is_parent:
            error_message = {
                "error_description": "User not found"
            }
            return HttpResponse(content=json.dumps(error_message), status=404, content_type="application/json")

        url, headers, body, status = self.create_token_response(request)

        if status == 200:
            body = json.loads(body)
            access_token = body.get("access_token")
            if access_token is not None:
                token = get_access_token_model().objects.get(
                    token=access_token)
                app_authorized.send(
                    sender=self, request=request,
                    token=token)
                body['id'] = str(token.user.id)
                body = json.dumps(body)

        response = HttpResponse(content=body, status=status)
        for k, v in headers.items():
            response[k] = v
        return response


class TeacherAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        teachers = Teacher.objects.all().values('user__pk')
        qs = User.objects.filter(pk__in=teachers)
        if self.q:
            qs = qs.filter(Q(first_name__icontains=self.q) | Q(
                last_name__icontains=self.q))
        return qs
