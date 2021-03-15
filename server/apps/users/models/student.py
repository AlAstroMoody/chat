from django.db import models


class Student(models.Model):
    base_user = models.OneToOneField(
        to='users.User',
        on_delete=models.CASCADE,
        related_name='student',
        verbose_name='id пользователя'
    )
    nickname = models.CharField(
        max_length=50,
        verbose_name='имя студента'
    )
    is_ready = models.BooleanField(
        default=False,
        verbose_name='готовность студента'
    )
    is_kicked = models.BooleanField(
        default=False,
        verbose_name='студент исключен'
    )
    connection_uuid = models.ForeignKey(
        to='rooms.Room',
        on_delete=models.CASCADE,
        verbose_name='уникальный идентификатор комнаты'
    )

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ('id',)

    def __str__(self):
        return self.nickname

    @classmethod
    def generate_username(cls, nickname, connection_uuid):
        return f'{nickname}_{connection_uuid}'
