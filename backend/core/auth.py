from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from apps.users.models import User
from django.contrib.auth.backends import ModelBackend
from django.utils import timezone
from ipware import get_client_ip

if TYPE_CHECKING:
    from django.http import HttpRequest


class AuthBackend(ModelBackend):
    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        **kwargs: Any,
    ):
        username = username or kwargs.get("email")
        assert request and username and password

        user = cast(
            User | None, super().authenticate(request, username=username, password=password)
        )
        if user is None:
            return user

        # Update user
        user.last_login = timezone.now()
        user.ip = get_client_ip(request)[0]
        user.save(update_fields=["last_login", "ip"])

        return user
