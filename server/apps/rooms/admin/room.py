from django.contrib import admin

from ..models.room import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'connection_uuid', 'trainer', 'max_round_time',
        'max_rounds_count', 'max_students_count', 'is_started', 'is_finished'
    )
