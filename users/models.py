import bcrypt
from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100, blank=True)
    password_hash = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)

    def set_password(self, raw_password):
        self.password_hash = bcrypt.hashpw(
            raw_password.encode("utf-8"), bcrypt.gensalt()
        ).decode()
        self.save()

    def check_password(self, raw_password):
        return bcrypt.checkpw(
            raw_password.encode("utf-8"),
            self.password_hash.encode()
        )

    def __str__(self):
        return self.email


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    users = models.ManyToManyField(User, related_name="roles")

    def __str__(self):
        return self.name


class BusinessElement(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class AccessRoleRule(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE)

    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)
