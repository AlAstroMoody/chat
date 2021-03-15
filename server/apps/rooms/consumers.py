from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.cache import cache

from apps.users.models import Student
from .constants import ChatConstants
from .models import Room, Round, Message
from .services.chat import Chat
from .services.reports import Report
from .tasks import timer_end


class ChatConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uuid = self.scope['url_route']['kwargs']['uuid']
        self.user = self.scope["user"]
        self.group_name = f'room-{self.uuid}'
        self.timer_round_is_active = False
        self.timer_training_is_active = False

    async def connect(self):
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        try:
            await Chat.validate_room(self.uuid, self.user)
        except DenyConnection as error:
            await self.send_json(error.args[0])
            await self.close()
        self.room = await self.get_room()
        self.username = await self.get_username()
        self.in_round = await self.current_round()
        await self.send_json({'room_info': await self.room_info()})
        await self.users_list()

    @database_sync_to_async
    def get_room(self):
        return Room.objects.get(connection_uuid=self.uuid)

    @database_sync_to_async
    def get_username(self):
        return self.user.get_username

    @database_sync_to_async
    def students_list(self):
        students_list = Student.objects.filter(
            connection_uuid__connection_uuid=self.uuid,
            is_kicked=False
        ).values_list('nickname', flat=True)
        return list(students_list)

    async def users_list(self):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'message_send',
                'users_list': await self.students_list()
            }
        )

    async def message_send(self, event):
        await self.send_json(event)

    async def room_info(self):
        return {
            'max_round_time': self.room.max_round_time,
            'max_rounds_count': self.room.max_rounds_count,
            'max_students_count': self.room.max_students_count,
            'is_allowed_to_send_message': await self.is_allowed_to_send_message()
        }

    @database_sync_to_async
    def current_round(self):
        rounds = Round.objects.filter(room=self.room)
        if bool(rounds.count()):
            in_round = Round.objects.filter(room=self.room).latest('id')
            return in_round
        return False

    @database_sync_to_async
    def is_allowed_to_send_message(self):
        # проверка, может ли юзер отправить сообщение в текущем раунде
        if not self.in_round:
            return False
        if self.user.is_student and self.is_round_timer_active() or self.user.is_trainer:
            messages_count = Message.objects.filter(
                author=self.user,
                in_round=self.in_round
            ).count()
            return not bool(messages_count)

    def is_round_timer_active(self):
        return cache.get(self.uuid)

    async def receive_json(self, content, **kwargs):
        # content должен содержать dict с ключами text, type(ready, start_training, start_round...)
        if 'type' in content:
            await self.user_command(content['type'])
        else:
            if await self.is_allowed_to_send_message():
                message = {
                    'type': 'message_send',
                    'author': self.username,
                    'text': content['text']
                }
                await self.channel_layer.group_send(
                    self.group_name,
                    message
                )
                if self.user.is_trainer:
                    await self.timer_round_start()
                await self.create_message(message)

    async def user_command(self, command):
        print(command)
        if command == 'end_training_timer':
            await self.end_training_timer()
        if self.user.is_trainer:
            if command == 'training_start':
                await self.training_start()
            if command == 'training_end':
                await self.training_end()
            if command == 'round_start' and self.timer_training_is_active == False:
                await self.round_start()
        else:
            if command == 'ready':
                await self.student_ready()

    @database_sync_to_async
    def create_message(self, message):
        Message.objects.create(
            author=self.user,
            text=message['text'],
            in_round=self.in_round
        )

    async def timer_round_start(self):
        self.timer_round_is_active = True
        cache.set(self.uuid, self.timer_round_is_active, self.room.max_round_time)

    async def timer_training_start(self):
        self.timer_round_is_active = True
        cache.set(
            self.group_name,
            self.timer_training_is_active,
            ChatConstants.TIMER_TRAINING_DURATION
        )

    def is_round_training_active(self):
        return cache.get(self.group_name)

    async def training_start(self):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'message_send',
                'message_to_all': ChatConstants.TRAINING_STARTED
            }
        )
        await self.room_training_start()
        try:
            timer_end(self.group_name)
        except Exception as err:
            print(err)

    async def end_training_timer(self):
        self.timer_round_is_active = False
        await self.choose_ready_students()

    @database_sync_to_async
    def choose_ready_students(self):
        all_active_students_in_room = Student.objects.filter(
            connection_uuid__connection_uuid=self.uuid,
            is_kicked=False
        )
        for student in all_active_students_in_room:
            if not student.is_ready:
                self.student_kick(student.base_user)

    @database_sync_to_async
    def student_kick(self, pk):
        student = Student.objects.get(base_user=pk)
        student.is_kicked = True
        student.save()

    @database_sync_to_async
    def room_training_start(self):
        self.room.is_started = True
        self.room.save()

    async def training_end(self):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'message_send',
                'message_to_all': ChatConstants.TRAINING_FINISHED
            }
        )
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'message_send',
                'report': await self.return_report()
            }
        )
        await self.kick_all()

    @database_sync_to_async
    def kick_all(self):
        all_active_students_in_room = Student.objects.filter(
            connection_uuid__connection_uuid=self.uuid,
            is_kicked=False
        )
        for student in all_active_students_in_room:
            self.student_kick(student.base_user)

    @database_sync_to_async
    def return_report(self):
        return Report._generate_report(self.uuid)

    async def student_ready(self):
        await self.change_student_status_ready()
        await self.users_list()

    @database_sync_to_async
    def change_student_status_ready(self):
        self.user.student.is_ready = True
        self.user.save()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def round_start(self):
        ...
