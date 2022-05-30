from typing import Any

from django.http import HttpResponse, HttpResponseRedirect
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.views import APIView

from virtual_agent.utils import EmptyResponse, ResponseWithStatusAndError

from .models import CheckMaterial


@extend_schema(
    tags=['Materials'],
    responses={'302': EmptyResponse, '4XX': ResponseWithStatusAndError},
)
class MaterialCheckAPIView(APIView):
    permission_classes = ()

    def get(
        self, request: Request, material_check_uuid: str, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        material_check = get_object_or_404(
            CheckMaterial.objects.all(), uuid=material_check_uuid
        )

        if request.user != material_check.user:
            raise PermissionDenied('You does not have access to this material')

        material_check.is_checked = True
        material_check.save()
        redirect_url = material_check.material.url

        return HttpResponseRedirect(redirect_url)
