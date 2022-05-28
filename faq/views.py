import csv
from io import StringIO
from typing import Any

from django.core.files.uploadedfile import InMemoryUploadedFile
from drf_spectacular.utils import extend_schema
from funcy import first, last
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course
from virtual_agent.utils import ResponseWithStatusAndError

from .models import FAQ
from .serializers import CreateFAQSerializer, FAQSerializer


@extend_schema(
    tags=['FAQ'],
    request=CreateFAQSerializer,
    responses={'200': FAQSerializer(many=True), '4XX': ResponseWithStatusAndError},
)
class FAQAPIView(APIView):
    permission_classes = ()

    def post(
        self, request: Request, course_uuid: str, *args: Any, **kwargs: Any
    ) -> Response:
        course = get_object_or_404(Course.objects.all(), uuid=course_uuid)
        request_serializer = CreateFAQSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        csv_file: InMemoryUploadedFile = request_serializer.validated_data['csv_file']
        content = StringIO(csv_file.read().decode('utf-8'))
        reader = csv.DictReader(content, delimiter=';')
        faqs = []
        for row in reader:
            print(row)
            question = first(row.values())
            answer = last(row.values())
            faqs.append(FAQ(question=question, answer=answer, course=course))
        course.faqs.all().delete()
        faqs = FAQ.objects.bulk_create(faqs)

        return Response(FAQSerializer(faqs, many=True).data)

    def get(
        self, request: Request, course_uuid: str, *args: Any, **kwargs: Any
    ) -> Response:
        course = get_object_or_404(Course.objects.all(), uuid=course_uuid)
        response_serializer = FAQSerializer(course.faqs, many=True)

        return Response(response_serializer.data)
