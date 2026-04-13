from django.contrib import admin

from .models import Camera, Incident, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "role", "created_at")
	search_fields = ("user__username", "user__email", "role")


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
	list_display = ("camera_code", "name", "location", "status", "last_active")
	list_filter = ("status", "location")
	search_fields = ("camera_code", "name", "location")
