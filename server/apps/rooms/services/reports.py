from itertools import groupby
from tempfile import NamedTemporaryFile

from django.db.models import Count, Q
from django.http import HttpResponse
from openpyxl import Workbook
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from apps.users.models import Student
from ..errors import RoomError
from ..models import Room


class Report:
    @staticmethod
    def _generate_report(connection_uuid):
        students = Student.objects.filter(
            connection_uuid__connection_uuid=connection_uuid,
            is_kicked=False
        ).annotate(
            correct_answers_cnt=Count(
                'base_user__message', filter=Q(base_user__message__is_selected=True)
            )
        ).values(
            'nickname',
            'correct_answers_cnt'
        ).order_by('-correct_answers_cnt')
        same_score_groups = [
            list(el) for _, el in groupby(students, lambda x: x['correct_answers_cnt'])
        ]
        rows = []
        for place, students_list in enumerate(same_score_groups, 1):
            student_names = ', '.join(student['nickname'] for student in students_list)
            student_score = students_list[0]['correct_answers_cnt']
            rows.append({
                'place': place,
                'student_names': student_names,
                'student_score': student_score
            })
        return rows

    @staticmethod
    def _validate(connection_uuid, token):
        auth = JWTAuthentication()
        try:
            user = auth.get_user(auth.get_validated_token(token))
        except InvalidToken:
            raise PermissionDenied({
                'error': RoomError.NO_ACCESS
            })
        if not user.is_trainer:
            raise PermissionDenied({
                'error': RoomError.NO_ACCESS
            })
        try:
            room = Room.objects.get(connection_uuid=connection_uuid)
        except Room.DoesNotExist:
            raise NotFound({
                'error': RoomError.ROOM_NOT_FOUND
            })
        if not room.is_finished:
            raise ValidationError({
                'error': RoomError.TRAINING_NOT_FINISHED
            })

    @classmethod
    def create_xlsx(cls, connection_uuid, token):
        cls._validate(connection_uuid, token)
        report = cls._generate_report(connection_uuid)
        wb = Workbook()
        ws = wb.active
        ws.append(['Место', 'Никнейм студента', 'Количество баллов'])
        for item in report:
            ws.append([item['place'], str(item['student_names']), item['student_score']])
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            tmp.seek(0)
            stream = tmp.read()
        return cls._return_file(stream)

    @staticmethod
    def _return_file(stream):
        response = HttpResponse(stream, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename=file.xlsx'
        return response
