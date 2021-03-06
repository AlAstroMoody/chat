# Generated by Django 3.1.1 on 2021-01-14 05:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='trainer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room', to=settings.AUTH_USER_MODEL, verbose_name='id тренера'),
        ),
        migrations.AddField(
            model_name='message',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='автор сообщения'),
        ),
        migrations.AddField(
            model_name='message',
            name='in_round',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='rooms.round', verbose_name='номер раунда'),
        ),
    ]
