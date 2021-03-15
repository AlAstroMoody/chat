from django.db import models


class Trainer(models.Model):
    base_user = models.OneToOneField(
        to='users.User',
        on_delete=models.CASCADE,
        related_name='trainer',
        verbose_name='id пользователя'
    )

    class Meta:
        verbose_name = 'Тренер'
        verbose_name_plural = 'Тренер'
        ordering = ('base_user',)

    def __str__(self):
        return self.base_user
