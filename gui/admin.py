from django.contrib import admin
from .models import CustomUser
from .models import RegistrationCode
from .models import Shelter
from .models import DogAdoptionPost


class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    ordering = ('role',)
    search_fields = ('role', 'username', 'email')
    list_display = ('username', 'email', 'role', 'registration_code')
    fields = ('username', 'email', 'role', 'registration_code')


class RegistrationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'username', 'is_activated')
    search_fields = ('code', 'username')


class ShelterAdmin(admin.ModelAdmin):
    list_display = ('name', 'working_hours', 'phone',)
    search_fields = ('name', 'working_hours', 'phone')


class DogAdoptionPostAdmin(admin.ModelAdmin):
    ordering = ('name',)
    list_display = ('name', 'age', 'gender', 'shelter')
    search_fields = ('code', 'username')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(RegistrationCode, RegistrationCodeAdmin)
admin.site.register(Shelter, ShelterAdmin)
admin.site.register(DogAdoptionPost, DogAdoptionPostAdmin)
