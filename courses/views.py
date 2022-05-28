from typing import Any

from drf_spectacular.utils import extend_schema
from funcy import lpluck_attr
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from virtual_agent.utils import ResponseWithStatusAndError

from .serializers import CourseSerializer


@extend_schema(
    tags=['Courses'],
    responses={'200': CourseSerializer(many=True), '4XX': ResponseWithStatusAndError},
)
class UserCoursesAPIView(APIView):
    permission_classes = ()

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        user_courses = lpluck_attr('course', user.moodle_groups.all())
        response_serializer = CourseSerializer(user_courses, many=True)

        return Response(response_serializer.data)
