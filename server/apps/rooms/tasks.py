from config.celery import app
from channels.layers import get_channel_layer


@app.task
def timer_end(group_name):
    print(group_name)
    channel_layer = get_channel_layer()
    channel_layer.group_send(
        group_name,
        {'type': 'end_training_timer'}
    )
    print("eg")
