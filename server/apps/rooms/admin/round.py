from django.contrib import admin

from ..models import Message
from ..models.round import Round


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', )

    inlines = (MessageInline, )
