from .models import Message
from users.models import Users


def add_message(from_user: Users, to_user: Users, message: str):
    message = Message(
        from_user=from_user,
        to_user=to_user,
        message=message
    )
    message.save()


def get_chat(from_user_id: int, to_user_id: int):
    return list(Message.objects.filter(
        from_user_id=from_user_id,
        to_user_id=to_user_id
    ).values())