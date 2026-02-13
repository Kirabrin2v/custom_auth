from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def login_required(permission_check=None):
    """
    Декоратор для методов класса (APIView) с проверкой авторизации и прав.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            try:
                user = getattr(request, "user", None)
                if not user or not hasattr(user, "roles"):
                    return Response(
                        {"detail": "Данные для входа не предоставлены"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

                # Проверка прав
                if (
                    permission_check and
                    not permission_check(request, *args, **kwargs)
                ):
                    return Response(
                        {"detail": "Недостаточно прав"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                # Вызов оригинального метода
                return view_func(self, request, *args, **kwargs)

            except Exception as e:
                return Response(
                    {"detail": f"Неожиданная ошибка: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return _wrapped_view
    return decorator
