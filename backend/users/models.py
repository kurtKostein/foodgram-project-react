#  users/models.py
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def _create_user(
            self, first_name, last_name, username, email, password, **kwargs
    ):
        values = [first_name, last_name, username, email, password]
        field_value_map = dict(zip(self.model.REQUIRED_FIELDS, values))
        for field_name, field_value in field_value_map.items():
            if not field_value:
                raise ValueError(f'Поле {field_name} должно быть заполнено')
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=self.normalize_email(email),
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
            self, first_name, last_name, username, email, password=None,
            **kwargs
    ):
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_superuser', False)
        return self._create_user(
            first_name, last_name, username, email, password, **kwargs
        )

    def create_superuser(
            self, first_name, last_name, username, email, password=None,
            **kwargs
    ):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        return self._create_user(
            first_name, last_name, username, email, password, **kwargs
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator

    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
        validators=[username_validator()]
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='Адрес элетронной почты',
        unique=True,
        validators=[EmailValidator()]
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'password']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

