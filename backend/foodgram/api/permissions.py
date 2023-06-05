from rest_framework.permissions import BasePermission, SAFE_METHODS

from users.models import ADMIN


class CustomPermission(BasePermission):
    """
    Проверяем и пропускаем дальше:
    1) На чтение - всех;
    2) На создание - авторизованных пользователей;
    3) На редактирование и удаление - авторов объектов, модераторов, админов.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or (request.method == 'POST' and request.user.is_authenticated)
            or (obj.author == request.user
                or request.user.is_authenticated
                and request.user.role == ADMIN)
        )
