#!/usr/bin/env python
"""
Example IoT Device Simulator

Simulates an IoT device sending temperature, humidity, and gas level data
to the FastAPI endpoint every 2 seconds.

Usage:
    python example_iot_device.py --api-key YOUR_API_KEY --interval 2000
"""
import requests
import time
import random
import argparse
from datetime import datetime


class IoTDeviceSimulator:
    def __init__(self, api_key, base_url="http://localhost:8001", interval=2):
        self.api_key = api_key
        self.base_url = base_url
        self.interval = interval
        self.endpoint = f"{base_url}/api/v1/sensor/reading"
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        self.sent_count = 0
        self.error_count = 0

    def generate_sensor_data(self):
        """Generate realistic sensor data."""
        return {
            "temperature": round(random.uniform(15, 30), 2),     # 15-30°C
            "humidity": round(random.uniform(30, 70), 2),         # 30-70%
            "gas_level": round(random.uniform(100, 500), 2)       # ppm
        }

    def send_reading(self, data):
        """Send a sensor reading to the API."""
        try:
            response = requests.post(
                self.endpoint,
                json=data,
                headers=self.headers,
                timeout=5
            )

            if response.status_code == 201:
                result = response.json()
                self.sent_count += 1
                timestamp = result['timestamp']
                print(
                    f"✓ [{datetime.now().strftime('%H:%M:%S')}] "
                    f"Reading sent - T={data['temperature']}°C, "
                    f"H={data['humidity']}%, G={data['gas_level']}ppm"
                )
                return True
            else:
                self.error_count += 1
                print(
                    f"✗ [{datetime.now().strftime('%H:%M:%S')}] "
                    f"Error: {response.status_code}"
                )
                if response.status_code == 401:
                    print("  Invalid API key")
                elif response.status_code == 403:
                    print("  Device is not active")
                else:
                    print(f"  {response.text}")
                return False

        except requests.exceptions.ConnectionError:
            self.error_count += 1
            print(
                f"✗ [{datetime.now().strftime('%H:%M:%S')}] "
                f"Connection failed - Is FastAPI running on {self.base_url}?"
            )
            return False
        except requests.exceptions.Timeout:
            self.error_count += 1
            print(
                f"✗ [{datetime.now().strftime('%H:%M:%S')}] "
                f"Request timeout"
            )
            return False
        except Exception as e:
            self.error_count += 1
            print(
                f"✗ [{datetime.now().strftime('%H:%M:%S')}] "
                f"Error: {str(e)}"
            )
            return False

    def run(self, duration=None):
        """Run the device simulator."""
        print("=" * 70)
        print("IoT Device Simulator")
        print("=" * 70)
        print(f"API Key:      {self.api_key[:20]}...")
        print(f"Base URL:     {self.base_url}")
        print(f"Interval:     {self.interval} seconds")
        if duration:
            print(f"Duration:     {duration} seconds")
        print("Status:       Running (Press Ctrl+C to stop)")
        print("=" * 70 + "\n")

        start_time = time.time()

        try:
            while True:
                # Check duration if specified
                if duration and (time.time() - start_time) > duration:
                    print("\nDuration reached, stopping...")
                    break

                # Generate and send data
                data = self.generate_sensor_data()
                self.send_reading(data)

                # Wait for the specified interval
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\n\nStopped by user")
        finally:
            self.print_summary()

    def print_summary(self):
        """Print summary statistics."""
        print("\n" + "=" * 70)
        print("Summary")
        print("=" * 70)
        print(f"Readings sent:    {self.sent_count}")
        print(f"Errors:           {self.error_count}")
        total = self.sent_count + self.error_count
        if total > 0:
            success_rate = (self.sent_count / total) * 100
            print(f"Success rate:     {success_rate:.1f}%")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="IoT Device Simulator for R-E-S-Q Backend"
    )
    parser.add_argument(
        "--api-key",
        required=True,
        help="Device API key (from create_iot_device command)"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8001",
        help="FastAPI base URL (default: http://localhost:8001)"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2,
        help="Interval between readings in seconds (default: 2)"
    )
    parser.add_argument(
        "--duration",
        type=float,
        help="Run for specified duration in seconds (optional)"
    )

    args = parser.parse_args()

    device = IoTDeviceSimulator(
        api_key=args.api_key,
        base_url=args.base_url,
        interval=args.interval
    )

    device.run(duration=args.duration)


if __name__ == "__main__":
    main()
