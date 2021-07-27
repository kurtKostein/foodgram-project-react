from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'username', 'email',)
    list_filter = ('last_name', 'email',)
