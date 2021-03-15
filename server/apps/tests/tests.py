from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.rooms.models import Round
from apps.rooms.services.reports import Report
from apps.users.models import User, Student, Role
from .factories import MessageFactory, StudentFactory, UserFactory, RoomFactory, RoundFactory


class ReportAPITests(APITestCase):
    ROUNDS_CNT = 4
    STUDENTS_CNT = 3
    ALL_ANSWERS_SELECTED = [1] * STUDENTS_CNT * ROUNDS_CNT
    ONE_ANSWER_NOT_SELECTED = ALL_ANSWERS_SELECTED[:-1] + [0]
    DIFFERENT_ANSWERS_COUNT = [0] * ROUNDS_CNT + ONE_ANSWER_NOT_SELECTED[ROUNDS_CNT:]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # создаём тренера
        cls.trainer = UserFactory(username='trainer_19')
        cls.trainer.set_password('password')
        cls.trainer.save()

        # получаем токен
        client = APIClient()
        response = client.post(reverse('trainer'), {
            'username': 'trainer_19',
            'password': 'password'
        })
        cls.token = response.data['access']

        # создаём комнату
        cls.room = RoomFactory(trainer=cls.trainer)
        cls.room.save()
        cls.connection_uuid = cls.room.connection_uuid

        # создаём раунды
        for i in range(cls.ROUNDS_CNT):
            in_round = RoundFactory(room=cls.room)
            in_round.save()
        cls.rounds = Round.objects.all()

        # создаём студентов
        for i in range(cls.STUDENTS_CNT):
            user = UserFactory(role=Role.STUDENT)
            user.save()
        users_th_student_role_ = User.objects.filter(role=Role.STUDENT)
        for user in users_th_student_role_:
            student = StudentFactory(
                connection_uuid=cls.room,
                base_user=user
            )
            student.save()
        cls.students = Student.objects.all()

    def test_all_message_is_selected(self):
        """
            создаем всем студентам верные сообщения
        """

        for student in self.students:
            for in_round in self.rounds:
                message = MessageFactory(
                    author=student.base_user,
                    in_round=in_round
                )
                message.save()

        # завершаем чемпионат
        self.room.is_finished = True
        self.room.save()
        data = Report._generate_report(self.connection_uuid)

        # возвращается список с одним словарем
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), 1)
        self.assertEqual(type(data[0]), dict)

        # у всех первое место
        self.assertEqual(data[0]['place'], 1)

        # и три верных ответов
        self.assertEqual(data[0]['student_score'], self.ROUNDS_CNT)

    def test_all_students_have_different_answer_amounts(self):
        """
            создаем всем студентам разное количество верных сообщений
        """

        for student in self.students:
            for in_round in self.rounds:
                message = MessageFactory(
                    author=student.base_user,
                    in_round=in_round,
                    is_selected=self.DIFFERENT_ANSWERS_COUNT.pop()
                )
                message.save()

        # завершаем чемпионат
        self.room.is_finished = True
        self.room.save()
        data = Report._generate_report(self.connection_uuid)

        # возвращается список с тремя словарем
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), self.STUDENTS_CNT)
        self.assertEqual(type(data[0]), dict)

        # места проставлены верно
        self.assertEqual(data[0]['place'], 1)
        self.assertEqual(data[1]['place'], 2)
        self.assertEqual(data[2]['place'], 3)

        # и проверяем количество верных ответов
        self.assertEqual(data[0]['student_score'], self.ROUNDS_CNT)
        self.assertEqual(data[1]['student_score'], self.ROUNDS_CNT - 1)
        self.assertEqual(data[2]['student_score'], 0)

    def test_two_students_have_same_amount_answers(self):
        """
            создаем двум студентам равное количество верных сообщений
        """

        # раздаём ответы студням
        for student in self.students:
            for in_round in self.rounds:
                message = MessageFactory(
                    author=student.base_user,
                    in_round=in_round,
                    is_selected=self.ONE_ANSWER_NOT_SELECTED.pop()
                )
                message.save()

        # завершаем чемпионат
        self.room.is_finished = True
        self.room.save()
        # generate_report(request, connection_uuid, ulr_token)
        data = Report._generate_report(self.connection_uuid)

        # возвращается список с двумя словарем
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), 2)
        self.assertEqual(type(data[0]), dict)

        # места проставлены верно
        self.assertEqual(data[0]['place'], 1)
        self.assertEqual(data[1]['place'], 2)

        # и проверяем количество верных ответов
        self.assertEqual(data[0]['student_score'], self.ROUNDS_CNT)
        self.assertEqual(data[1]['student_score'], self.ROUNDS_CNT - 1)

    def test_room_not_exist(self):
        """
        GET-запрос, комната не существует:
        """

        # ошибочный номер комнаты для теста
        wrong_uuid = 'e2b6dc24-9048-4d85-a70d-337f79f18149'
        url = reverse('report', kwargs={'uuid': wrong_uuid, 'token': self.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_room_forbidden(self):
        """
        GET-запрос, комната существует, токен ошибочный:
        """
        wrong_token = get_random_string()
        url = reverse('report', kwargs={'uuid': self.connection_uuid, 'token': wrong_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_room_exist_but_not_finished(self):
        """
        GET-запрос, комната существует и тренинг не завершён:
        """

        url = reverse('report', kwargs={'uuid': self.connection_uuid, 'token': self.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_room_exist_and_finished(self):
        """
        GET-запрос, комната существует и тренинг завершён:
        """
        self.room.is_finished = True
        self.room.save()
        url = reverse('report', kwargs={'uuid': self.connection_uuid, 'token': self.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
