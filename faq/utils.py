import csv
from io import StringIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from funcy import first, last

from courses.models import Course

from .models import FAQ


def create_faq_from_csv(csv_file: InMemoryUploadedFile, course: Course):
    content = StringIO(csv_file.read().decode('utf-8'))
    reader = csv.DictReader(content, delimiter=';')
    faqs = []
    for row in reader:
        question = first(row.values())
        answer = last(row.values())
        faqs.append(FAQ(question=question, answer=answer, course=course))
    course.faqs.all().delete()
    return FAQ.objects.bulk_create(faqs)
