import re

from django.core.validators import validate_email as valid_email
from rest_framework.exceptions import ValidationError

from users.models import User


def validate_username(value):
    regex = re.compile(r'^[\w.@+-]+')
    if str(value).lower() == 'me':
        raise ValidationError('Недопустимое имя пользователя.')
    elif not regex.match(value):
        raise ValidationError('Имя содержит недопустимые символы.')


def validate_username_exists(value):
    if User.objects.filter(username=value).exists():
        raise ValidationError('Такой пользователь уже существует')


def validate_email(value):
    valid_email(value)
    if User.objects.filter(email=value).exists():
        raise ValidationError('Пользователь с такой почтой '
                              'уже зарегестрирован')
    elif not valid_email(value):
        raise ValidationError('Некорректнаый адрес почты')
