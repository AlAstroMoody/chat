import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Room(models.Model):
    class Constraints:
        MIN_ROUND_TIME = 15
        MAX_ROUND_TIME = 60
        MIN_ROUNDS_COUNT = 2
        MAX_STUDENTS_COUNT = 15
        MIN_STUDENTS_COUNT = 2

    connection_uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name='уникальный идентификатор комнаты'
    )
    trainer = models.ForeignKey(
        to='users.User',
        on_delete=models.CASCADE,
        verbose_name='id тренера',
        related_name='room'
    )
    max_round_time = models.PositiveSmallIntegerField(
        verbose_name='максимальное время раунда',
        validators=[
            MaxValueValidator(Constraints.MAX_ROUND_TIME),
            MinValueValidator(Constraints.MIN_ROUND_TIME)
        ]
    )
    max_rounds_count = models.PositiveSmallIntegerField(
        verbose_name='максимальное количество раундов',
        validators=[
            MinValueValidator(Constraints.MIN_ROUNDS_COUNT)
        ]
    )
    max_students_count = models.PositiveSmallIntegerField(
        verbose_name='максимальное количество студентов',
        validators=[
            MaxValueValidator(Constraints.MAX_STUDENTS_COUNT),
            MinValueValidator(Constraints.MIN_STUDENTS_COUNT)
        ]
    )
    is_started = models.BooleanField(
        default=False,
        verbose_name='тренинг начался'
    )
    is_finished = models.BooleanField(
        default=False,
        verbose_name='тренинг закончился'
    )

    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'

    def __str__(self):
        return str(self.connection_uuid)
