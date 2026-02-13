from rest_framework.permissions import BasePermission
from users.models import AccessRoleRule, BusinessElement


def is_admin(request):
    """
    Возвращает True, если у пользователя есть роль 'admin'.
    """
    user = request.user
    if not user:
        return False
    return user.roles.filter(name="admin").exists()


class CustomPermission(BasePermission):
    """
    Проверка доступа к объекту через таблицу AccessRoleRule.
    """

    def has_permission(self, request, view):
        # Пользователь не авторизован
        if not hasattr(request, "user") or request.user is None:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        roles = user.role_set.all()
        element = BusinessElement.objects.get(name=obj.__class__.__name__)

        rules = AccessRoleRule.objects.filter(role__in=roles, element=element)

        for rule in rules:
            if request.method == "GET":
                if rule.read_all_permission:
                    return True
                if rule.read_permission and obj.owner_id == user.id:
                    return True

            if request.method == "POST" and rule.create_permission:
                return True

            if request.method in ["PUT", "PATCH"]:
                if rule.update_all_permission:
                    return True
                if rule.update_permission and obj.owner_id == user.id:
                    return True

            if request.method == "DELETE":
                if rule.delete_all_permission:
                    return True
                if rule.delete_permission and obj.owner_id == user.id:
                    return True

        return False
