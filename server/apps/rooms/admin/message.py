from django.contrib import admin

from ..models.message import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'text', 'in_round',
        'is_selected', 'created_at'
    )
