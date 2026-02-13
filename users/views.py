from datetime import datetime, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import jwt

from .authentication import JWTAuthentication
from .decorators import login_required
from .permissions import is_admin
from .models import AccessRoleRule, User
from .serializers import (
    AccessRoleRuleSerializer,
    RegisterSerializer,
    LoginSerializer
)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"id": user.id, "email": user.email}, status=201)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Некорректные данные для входа"},
                status=401
            )

        if not user.check_password(password):
            return Response(
                {"detail": "Некорректные данные для входа"},
                status=401
            )

        payload = {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return Response({"token": token})


class LogoutView(APIView):
    """
    На сервере нет хранения сессий,
    клиент просто удаляет токен.
    """
    def post(self, request):
        return Response(
            {"detail": "Успешный выход"},
            status=status.HTTP_200_OK
        )


class AccessRoleRuleAPI(APIView):
    authentication_classes = [JWTAuthentication]

    @login_required(permission_check=is_admin)
    def get(self, request):
        rules = AccessRoleRule.objects.all()
        serializer = AccessRoleRuleSerializer(rules, many=True)
        return Response(serializer.data)

    @login_required(permission_check=is_admin)
    def post(self, request):
        serializer = AccessRoleRuleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @login_required(permission_check=is_admin)
    def put(self, request, rule_id):
        try:
            rule = AccessRoleRule.objects.get(id=rule_id)
        except AccessRoleRule.DoesNotExist:
            return Response(
                {"detail": "Правило не найдено"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AccessRoleRuleSerializer(
            rule,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserProfileAPI(APIView):
    """
    Управление профилем пользователя:
    - GET: получить данные о себе
    - PUT/PATCH: обновить профиль
    - DELETE: мягкое удаление аккаунта
    """
    authentication_classes = [JWTAuthentication]

    @login_required()
    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "patronymic": user.patronymic,
            "is_active": user.is_active,
        }
        return Response(data)

    @login_required()
    def put(self, request):
        user = request.user
        serializer = RegisterSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        password = request.data.get("password")
        if password:
            user.set_password(password)

        serializer.save()
        return Response({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "patronymic": user.patronymic
        })

    @login_required()
    def delete(self, request):
        user = request.user
        # мягкое удаление
        user.is_active = False
        user.save()
        return Response(
            {"detail": "Аккаунт деактивирован и вы вышли из системы"},
            status=status.HTTP_200_OK
        )
