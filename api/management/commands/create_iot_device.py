"""
Management command to create IoT devices with API keys.

Usage:
    python manage.py create_iot_device --device-id DEVICE_001 --name "Sensor 1" --location "Room A"
"""
import secrets
from django.core.management.base import BaseCommand
from api.models import IoTDevice


class Command(BaseCommand):
    help = "Create IoT devices with API keys"

    def add_arguments(self, parser):
        parser.add_argument(
            "--device-id",
            type=str,
            required=True,
            help="Unique device identifier",
        )
        parser.add_argument(
            "--name",
            type=str,
            required=True,
            help="Device name",
        )
        parser.add_argument(
            "--location",
            type=str,
            required=True,
            help="Device location",
        )
        parser.add_argument(
            "--device-type",
            type=str,
            default="sensor",
            help="Device type (default: sensor)",
        )

    def handle(self, *args, **options):
        device_id = options["device_id"]
        name = options["name"]
        location = options["location"]
        device_type = options["device_type"]

        # Check if device already exists
        if IoTDevice.objects.filter(device_id=device_id).exists():
            self.stdout.write(
                self.style.ERROR(f"Device with ID '{device_id}' already exists")
            )
            return

        # Generate secure API key
        api_key = f"iot_{secrets.token_urlsafe(32)}"

        # Create device
        device = IoTDevice.objects.create(
            device_id=device_id,
            name=name,
            location=location,
            device_type=device_type,
            api_key=api_key,
        )

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Device created successfully!\n")
        )
        self.stdout.write(f"Device ID:    {device.device_id}")
        self.stdout.write(f"Name:         {device.name}")
        self.stdout.write(f"Location:     {device.location}")
        self.stdout.write(f"Device Type:  {device.device_type}")
        self.stdout.write(self.style.WARNING(f"\nAPI Key:      {api_key}"))
        self.stdout.write(
            self.style.WARNING(
                "\n⚠️  Keep this API key safe! It will not be displayed again.\n"
            )
        )
