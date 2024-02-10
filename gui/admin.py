from django.contrib import admin
from .models import CustomUser
from .models import RegistrationCode


class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    ordering = ('role',)
    search_fields = ('role', 'username', 'email')  # Include additional search fields if needed
    list_display = ('username', 'email', 'role', 'registration_code')  # Add fields to be displayed in the list view
    fields = ('username', 'email', 'role', 'registration_code')  # Include fields to be displayed in the detail view


class RegistrationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'username', 'is_activated')
    search_fields = ('code', 'username')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(RegistrationCode, RegistrationCodeAdmin)
