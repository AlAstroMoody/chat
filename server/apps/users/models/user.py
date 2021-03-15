from django.contrib.auth.models import AbstractUser
from django.db import models


class Role:
    TRAINER = 'trainer'
    STUDENT = 'student'
    CHOICES = (
        (TRAINER, 'trainer'),
        (STUDENT, 'student'),
    )


class User(AbstractUser):
    role = models.CharField(
        max_length=255,
        choices=Role.CHOICES,
        default=Role.TRAINER,
        verbose_name='роль пользователя'
    )

    @property
    def is_trainer(self):
        return self.role == Role.TRAINER

    @property
    def is_student(self):
        return self.role == Role.STUDENT

    @property
    def get_username(self):
        return self.username if self.is_trainer else self.student.nickname

    def __str__(self):
        return str(self.id)
