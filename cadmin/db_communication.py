from cadmin.models import CAdmin
import hashlib
import jwt
from ystories.settings import SECRET_KEY
from time import time


def get_admin(**kwargs) -> CAdmin:
    return CAdmin.objects.filter(
        **kwargs
    ).first()


def add_admin(values: dict) -> str:
    token = jwt.encode({
            'nickname': values['login'],
            'timestamp': str(time())
        }, key=SECRET_KEY)
    cadmin = CAdmin(
        login=values['login'],
        password=hashlib.sha256(values['password'].encode("utf-8")).hexdigest(),
        token=token
    )
    cadmin.save()
    return token


def get_all_admins():
    return [{
        'id': admin.id,
        'login': admin.login
    } for admin in CAdmin.objects.filter().all()]