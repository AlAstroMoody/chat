from django.db import models


class Message(models.Model):
    author = models.ForeignKey(
        to='users.User',
        on_delete=models.CASCADE,
        verbose_name='автор сообщения'
    )
    text = models.TextField(
        verbose_name='текст сообщения'
    )
    in_round = models.ForeignKey(
        to='rooms.Round',
        on_delete=models.CASCADE,
        verbose_name='номер раунда',
        related_name='messages'
    )
    is_selected = models.BooleanField(
        default=False,
        verbose_name='сообщение отмечено как верное'
    )
    created_at = models.DateTimeField(
        verbose_name='время создания сообщения',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ('id',)

    def __str__(self):
        return self.text
