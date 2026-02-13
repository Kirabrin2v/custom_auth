import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User
from jwt import ExpiredSignatureError, InvalidTokenError

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split()
            if prefix.lower() != "bearer":
                raise AuthenticationFailed("Некорректный префикс")
        except ValueError:
            raise AuthenticationFailed("Некорректный заголовок")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except ExpiredSignatureError:
            raise AuthenticationFailed("Истёк срок годности токена")
        except InvalidTokenError:
            raise AuthenticationFailed("Некорректный токен")

        try:
            user = User.objects.get(id=payload["user_id"], is_active=True)
        except User.DoesNotExist:
            raise AuthenticationFailed("Пользователь не найден")

        return (user, None)
