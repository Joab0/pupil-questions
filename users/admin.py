from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        "email",
        "first_name",
        "last_name",
        "created_at",
        "last_login",
        "ip",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informações pessoais", {"fields": ("first_name", "last_name")}),
        (
            "Permissões",
            {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)
