from rest_framework import serializers
from .models import AccessRoleRule, Role, BusinessElement, User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "patronymic",
            "password"
        )

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class AccessRoleRuleSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Role.objects.all()
    )
    element = serializers.SlugRelatedField(
        slug_field="name",
        queryset=BusinessElement.objects.all()
    )

    class Meta:
        model = AccessRoleRule
        fields = [
            "id",
            "role",
            "element",
            "read_permission",
            "read_all_permission",
            "create_permission",
            "update_permission",
            "update_all_permission",
            "delete_permission",
            "delete_all_permission",
        ]
