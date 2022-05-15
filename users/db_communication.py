from .models import Users, UserSubscriptions


def is_nickname_exists(nickname: str) -> bool:
    user = Users.objects.filter(
        nickname=nickname
    ).first()
    if user is None:
        return False
    return True


def add_user(nickname: str, token: str, password: str = '',
             phone_number: str = None, email: str = None, is_admin=False):
    user = Users(
        nickname=nickname,
        password=password,
        token=token,
        phone_number=phone_number,
        email=email,
        is_admin=is_admin
    )
    user.save()


def get_user(**kwargs) -> Users:
    return Users.objects.filter(
        **kwargs
    ).first()


def update_phone_number(nickname, phone):
    user = Users.objects.get(nickname=nickname)
    user.phone_number = phone
    user.save()


def update_code(nickname, code):
    user = Users.objects.get(nickname=nickname)
    user.sms_code = code
    user.save()


def update_phone_status(nickname, phone_status):
    user = Users.objects.get(nickname=nickname)
    user.is_phone_confirmed = phone_status
    user.save()


def update_password(token, password):
    user = Users.objects.get(token=token)
    user.password = password
    user.save()


def update_description(token, full_name=None, nickname=None, description=None, gender=None, birthday=None, photo=None):
    user = Users.objects.get(token=token)
    if full_name:
        user.full_name = full_name
    if nickname:
        user.nickname = nickname
    if description:
        user.description = description
    if gender:
        user.gender = gender
    if birthday:
        user.birthday = birthday
    if photo:
        user.photo = photo
    user.save()


def subscribe_unsubscribe(token, sub_id):
    relation = UserSubscriptions.objects.filter(user_subscriber=get_user(token=token)).first()
    if relation:
        relation.delete()
    else:
        sub = UserSubscriptions(user_subscriber=get_user(token=token), user_subscription=get_user(id=sub_id))
        sub.save()
    return not relation


def get_subscribers(user_id):
    return list(map(lambda x: x.user_subscriber,
                    list(UserSubscriptions.objects.filter(user_subscription=user_id).all())))


def get_subscriptions(user_id):
    return list(map(lambda x: x.user_subscription,
                    UserSubscriptions.objects.filter(user_subscriber=user_id).all()))
