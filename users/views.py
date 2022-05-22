from typing import Any

from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from virtual_agent.utils import EmptyResponse, ResponseWithStatusAndError

from .serializers import UserLoginRequestSerializer


@extend_schema(
    tags=['User'],
    request=UserLoginRequestSerializer,
    responses={'200': EmptyResponse, '4XX': ResponseWithStatusAndError},
)
class UserLoginView(APIView):
    authentication_classes = ()
    permission_classes = ()

    @csrf_exempt
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = UserLoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if user and user.is_active:
            login(request, user)
            return Response()

        raise NotAuthenticated('Authentication credentials are invalid')


@extend_schema(
    tags=['User'], responses={'200': EmptyResponse, '4XX': ResponseWithStatusAndError}
)
class UserLogoutView(APIView):
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        logout(request)
        return Response()
