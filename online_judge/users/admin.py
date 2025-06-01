from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role', 'my_saved_problems')}),
    )
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('role',)  # role is read-only for non-superusers
        return super().get_readonly_fields(request, obj)


admin.site.register(CustomUser, CustomUserAdmin)

# Register your models here.
