from rest_framework.generics import CreateAPIView

from ..serializers import StudentSerializer


class StudentView(CreateAPIView):
    serializer_class = StudentSerializer
