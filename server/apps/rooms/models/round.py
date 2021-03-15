from django.db import models


class Round(models.Model):
    room = models.ForeignKey(
        to='rooms.Room',
        on_delete=models.CASCADE,
        related_name='round',
        verbose_name='комната, в которой проводится раунд'
    )

    class Meta:
        verbose_name = 'Раунд'
        verbose_name_plural = 'Раунды'
        ordering = ('id',)

    def __str__(self):
        return str(self.id)
