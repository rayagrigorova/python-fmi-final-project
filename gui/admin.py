from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    ordering = ('role',)
    search_fields = ('role', 'username', 'email')  # Include additional search fields if needed
    list_display = ('username', 'email', 'role', 'registration_code')  # Add fields to be displayed in the list view
    fields = ('username', 'email', 'role', 'registration_code')  # Include fields to be displayed in the detail view


admin.site.register(CustomUser, CustomUserAdmin)
