from django.contrib import admin

from apps.common.models import BaseDBModel


class BaseDBModelAdmin(admin.ModelAdmin):
    def created_at(self, obj: BaseDBModel):
        return obj.created_at

    created_at.admin_order_field = "id"
    created_at.short_description = "Criado em"
