from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from apps.common.models import BaseDBModel


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email deve ser fornecido")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser requires is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser requires is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(BaseDBModel, AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        ordering = ["-id"]

    email = models.EmailField("E-mail", unique=True)
    first_name = models.CharField("Nome", max_length=30)
    last_name = models.CharField("Sobrenome", max_length=30)
    ip = models.GenericIPAddressField(null=True)
    updated_at = models.DateTimeField("Última alteração", auto_now=True)
    is_active = models.BooleanField("Ativo", default=True)
    is_staff = models.BooleanField("Staff", default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
