from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin 
from .models import User

# admin.site.register(User, UserAdmin)

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        additional_fields = ('is_42_user', 'id_42', 'uuid', 'rank', 'status', 'friends', 'profile_pic')
        self.fieldsets = BaseUserAdmin.fieldsets + (
            ('Properties', {'fields': additional_fields}),
        )
        self.list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_42_user', 'rank', 'status', 'uuid', 'profile_pic')
        self.list_filter = BaseUserAdmin.list_filter + ('is_42_user', 'status')
        self.search_fields = BaseUserAdmin.search_fields + ('id_42', 'uuid')