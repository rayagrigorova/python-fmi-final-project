from django.contrib import admin
from .models import CustomUser, Comment, PostSubscription
from .models import RegistrationCode
from .models import Shelter
from .models import DogAdoptionPost
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
    list_display = ('name', 'working_hours', 'phone', 'user')
    search_fields = ('name', 'working_hours', 'phone', 'user')


class DogAdoptionPostAdmin(admin.ModelAdmin):
    ordering = ('name',)
    list_display = ('name', 'age', 'gender', 'shelter', 'adoption_stage')
    search_fields = ('code', 'username')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('display_author', 'display_post', 'content',)

    # 'obj' is an object of type 'Comment' - the 'obj' parameter refers to the object managed by the admin interface
    def display_author(self, obj):
        return obj.author.username

    # Determine the text description that will appear for the column
    display_author.short_description = 'Author'

    def display_post(self, obj):
        return obj.post.name

    display_post.short_description = 'Post'


class PostSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('display_user', 'display_post', 'is_active',)

    def display_user(self, obj):
        return obj.user.username

    display_user.short_description = 'User'

    def display_post(self, obj):
        return obj.post.name

    display_post.short_description = 'Post'


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(RegistrationCode, RegistrationCodeAdmin)
admin.site.register(Shelter, ShelterAdmin)
admin.site.register(DogAdoptionPost, DogAdoptionPostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PostSubscription, PostSubscriptionAdmin)
