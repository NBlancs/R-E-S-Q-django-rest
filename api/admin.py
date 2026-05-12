from django.contrib import admin

from .models import Camera, Incident, UserProfile, IoTDevice, SensorReading


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "role", "created_at")
	search_fields = ("user__username", "user__email", "role")


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
	list_display = ("camera_code", "name", "location", "status", "last_active")
	list_filter = ("status", "location")
	search_fields = ("camera_code", "name", "location")


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
	list_display = (
		"incident_code",
		"incident_type",
		"location",
		"status",
		"time_reported",
	)
	list_filter = ("incident_type", "status", "detection_method")
	search_fields = ("incident_code", "location", "notes")


@admin.register(IoTDevice)
class IoTDeviceAdmin(admin.ModelAdmin):
	list_display = ("device_id", "name", "location", "status", "device_type", "last_reading")
	list_filter = ("status", "device_type", "location")
	search_fields = ("device_id", "name", "location")
	readonly_fields = ("api_key", "created_at", "updated_at", "last_reading")
	fieldsets = (
		("Device Information", {
			"fields": ("device_id", "name", "location", "device_type", "status")
		}),
		("API Key", {
			"fields": ("api_key",),
			"classes": ("collapse",),
		}),
		("Timestamps", {
			"fields": ("last_reading", "created_at", "updated_at"),
			"classes": ("collapse",),
		}),
	)

	def get_readonly_fields(self, request, obj=None):
		# api_key is always read-only, but created_at/updated_at only when editing
		if obj:  # Editing an existing object
			return self.readonly_fields
		return ["api_key"]


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
	list_display = ("device", "temperature", "humidity", "gas_level", "timestamp")
	list_filter = ("device", "timestamp")
	search_fields = ("device__device_id", "device__name")
	readonly_fields = ("timestamp",)
	date_hierarchy = "timestamp"
