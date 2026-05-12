from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Camera, Incident, UserProfile, IoTDevice, SensorReading


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["username", "email", "role", "avatar"]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, default=UserProfile.ROLE_BFP)
    avatar = serializers.URLField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def create(self, validated_data):
        email = validated_data["email"].strip().lower()
        username = (validated_data.get("username") or "").strip()
        role = validated_data.get("role", UserProfile.ROLE_BFP)
        avatar = validated_data.get("avatar", "")

        if not username:
            base = email.split("@")[0]
            candidate = base
            counter = 1
            while User.objects.filter(username__iexact=candidate).exists():
                counter += 1
                candidate = f"{base}{counter}"
            username = candidate

        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data["password"],
        )
        UserProfile.objects.create(user=user, role=role, avatar=avatar)
        return user


class CameraSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Camera
        fields = [
            "id",
            "camera_code",
            "name",
            "location",
            "status",
            "last_active",
            "footage_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class IncidentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    camera_code = serializers.CharField(source="camera.camera_code", read_only=True)
    reported_by_username = serializers.CharField(source="reported_by.username", read_only=True)

    class Meta:
        model = Incident
        fields = [
            "id",
            "incident_code",
            "incident_type",
            "location",
            "detection_method",
            "time_reported",
            "status",
            "camera",
            "camera_code",
            "reported_by",
            "reported_by_username",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "reported_by"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["reported_by"] = request.user
        return super().create(validated_data)


class SensorReadingSerializer(serializers.ModelSerializer):
	device_id = serializers.CharField(source="device.device_id", read_only=True)

	class Meta:
		model = SensorReading
		fields = ["id", "device", "device_id", "temperature", "humidity", "gas_level", "timestamp"]
		read_only_fields = ["timestamp"]


class IoTDeviceSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(read_only=True)
	readings_count = serializers.SerializerMethodField()
	latest_reading = serializers.SerializerMethodField()

	class Meta:
		model = IoTDevice
		fields = [
			"id",
			"device_id",
			"name",
			"location",
			"device_type",
			"status",
			"api_key",
			"last_reading",
			"readings_count",
			"latest_reading",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["api_key", "created_at", "updated_at", "last_reading"]

	def get_readings_count(self, obj):
		return obj.readings.count()

	def get_latest_reading(self, obj):
		latest = obj.readings.first()
		if latest:
			return SensorReadingSerializer(latest).data
		return None
