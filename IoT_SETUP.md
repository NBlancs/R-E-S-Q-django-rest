# IoT Integration Guide

This guide explains how to connect and use IoT devices with the R-E-S-Q backend.

## Overview

The system consists of:
- **Django Backend** (port 8000): Stores sensor data in the database
- **FastAPI Service** (port 8001): Receives real-time sensor data from IoT devices
- **API Key Authentication**: Each device has a unique API key for secure communication

## Setup

### 1. Start Both Services

```bash
python run_all.py
```

This will start:
- Django: http://localhost:8000
- FastAPI: http://localhost:8001
- API Docs: http://localhost:8001/docs (interactive Swagger UI)

### 2. Create an IoT Device

Use Django management command to register a new device:

```bash
python manage.py create_iot_device \
  --device-id SENSOR_001 \
  --name "Room A Temperature Sensor" \
  --location "Building A, Room A" \
  --device-type "temperature_humidity_gas"
```

**Output:**
```
✓ Device created successfully!

Device ID:    SENSOR_001
Name:         Room A Temperature Sensor
Location:     Building A, Room A
Device Type:  temperature_humidity_gas

API Key:      iot_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

⚠️  Keep this API key safe! It will not be displayed again.
```

### 3. Manage Devices in Admin Panel

Access Django admin: http://localhost:8000/admin/

Login with your admin credentials and navigate to:
- **IoT Devices**: View, create, and manage devices
- **Sensor Readings**: View all recorded sensor data

## API Endpoints

### Submit Sensor Reading

**Endpoint:** `POST /api/v1/sensor/reading`

**Headers:**
- `X-API-Key: your-device-api-key`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "temperature": 22.5,
  "humidity": 45.3,
  "gas_level": 150.0
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "device_id": "SENSOR_001",
  "temperature": 22.5,
  "humidity": 45.3,
  "gas_level": 150.0,
  "timestamp": "2026-05-13T12:34:56.789Z"
}
```

### Get Device Status

**Endpoint:** `GET /api/v1/device/status`

**Headers:**
- `X-API-Key: your-device-api-key`

**Response:**
```json
{
  "device_id": "SENSOR_001",
  "name": "Room A Temperature Sensor",
  "status": "active",
  "last_reading": "2026-05-13T12:34:56.789Z"
}
```

### Get Device Readings

**Endpoint:** `GET /api/v1/device/readings?limit=10`

**Headers:**
- `X-API-Key: your-device-api-key`

**Query Parameters:**
- `limit`: Number of readings to return (default: 10, max: 100)

**Response:**
```json
{
  "device_id": "SENSOR_001",
  "count": 10,
  "readings": [
    {
      "id": 10,
      "temperature": 22.5,
      "humidity": 45.3,
      "gas_level": 150.0,
      "timestamp": "2026-05-13T12:34:56.789Z"
    },
    ...
  ]
}
```

## Example: Send Sensor Data Every 2 Seconds

### Using cURL

```bash
#!/bin/bash

API_KEY="iot_your_device_api_key_here"
BASE_URL="http://localhost:8001"

# Function to send sensor data
send_sensor_data() {
  TEMP=$1
  HUMIDITY=$2
  GAS=$3
  
  curl -X POST "$BASE_URL/api/v1/sensor/reading" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"temperature\": $TEMP,
      \"humidity\": $HUMIDITY,
      \"gas_level\": $GAS
    }"
}

# Send data every 2 seconds
while true; do
  TEMP=$(awk -v min=15 -v max=30 'BEGIN{srand(); print min+rand()*(max-min)}')
  HUMIDITY=$(awk -v min=30 -v max=70 'BEGIN{srand(); print min+rand()*(max-min)}')
  GAS=$(awk -v min=100 -v max=500 'BEGIN{srand(); print min+rand()*(max-min)}')
  
  echo "Sending: T=$TEMP, H=$HUMIDITY, G=$GAS"
  send_sensor_data $TEMP $HUMIDITY $GAS
  
  sleep 2
done
```

### Using Python

```python
import requests
import time
import random

API_KEY = "iot_your_device_api_key_here"
BASE_URL = "http://localhost:8001"
ENDPOINT = f"{BASE_URL}/api/v1/sensor/reading"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def send_sensor_data(temperature, humidity, gas_level):
    """Send sensor reading to the API."""
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "gas_level": gas_level
    }
    
    try:
        response = requests.post(ENDPOINT, json=data, headers=headers, timeout=5)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Reading recorded: {result['timestamp']}")
            return True
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error: {e}")
        return False

def main():
    """Send sensor readings every 2 seconds."""
    print("Starting sensor data transmission...")
    print(f"API Key: {API_KEY}")
    print("Sending every 2 seconds (Ctrl+C to stop)\n")
    
    try:
        while True:
            # Simulate sensor readings
            temperature = random.uniform(15, 30)  # 15-30°C
            humidity = random.uniform(30, 70)      # 30-70%
            gas_level = random.uniform(100, 500)   # ppm
            
            send_sensor_data(temperature, humidity, gas_level)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\nStopped")

if __name__ == "__main__":
    main()
```

### Using Node.js

```javascript
const axios = require('axios');

const API_KEY = 'iot_your_device_api_key_here';
const BASE_URL = 'http://localhost:8001';
const ENDPOINT = `${BASE_URL}/api/v1/sensor/reading`;

const headers = {
  'X-API-Key': API_KEY,
  'Content-Type': 'application/json'
};

async function sendSensorData(temperature, humidity, gasLevel) {
  const data = {
    temperature,
    humidity,
    gas_level: gasLevel
  };
  
  try {
    const response = await axios.post(ENDPOINT, data, { headers });
    console.log(`✓ Reading recorded: ${response.data.timestamp}`);
    return true;
  } catch (error) {
    console.error(`✗ Error: ${error.response?.status} - ${error.message}`);
    return false;
  }
}

async function main() {
  console.log('Starting sensor data transmission...');
  console.log(`API Key: ${API_KEY}`);
  console.log('Sending every 2 seconds (Ctrl+C to stop)\n');
  
  try {
    while (true) {
      const temperature = 15 + Math.random() * 15;  // 15-30°C
      const humidity = 30 + Math.random() * 40;      // 30-70%
      const gasLevel = 100 + Math.random() * 400;    // ppm
      
      await sendSensorData(temperature, humidity, gasLevel);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  } catch (error) {
    console.log('\n\nStopped');
  }
}

main();
```

## Data Storage & Retrieval

All sensor readings are automatically stored in the Django database.

### Query in Django Shell

```bash
python manage.py shell
```

```python
from api.models import IoTDevice, SensorReading

# Get a device
device = IoTDevice.objects.get(device_id='SENSOR_001')

# Get all readings for the device
readings = device.readings.all()

# Get latest 10 readings
latest = device.readings.all()[:10]

# Get readings from the last hour
from django.utils import timezone
from datetime import timedelta

one_hour_ago = timezone.now() - timedelta(hours=1)
recent_readings = device.readings.filter(timestamp__gte=one_hour_ago)

# Get average values
avg_temp = readings.aggregate(avg=models.Avg('temperature'))['avg']
avg_humidity = readings.aggregate(avg=models.Avg('humidity'))['avg']
```

### REST API (Django)

You can also query the readings through the Django REST API:

```bash
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/iot-devices/
```

## Database Models

### IoTDevice
```
- device_id (unique)
- name
- location
- device_type
- status (active/inactive/maintenance)
- api_key (unique, auto-generated)
- last_reading (timestamp)
- created_at
- updated_at
```

### SensorReading
```
- device (ForeignKey to IoTDevice)
- temperature (float)
- humidity (float)
- gas_level (float)
- timestamp (auto-set to now)
```

## Monitoring & Analytics

The system stores all readings with timestamps, allowing you to:
- Track sensor history
- Generate reports
- Create alerts on threshold violations
- Monitor device health (last_reading)

## API Key Security

⚠️ **Important:**
- Store API keys securely (use environment variables)
- Do not commit API keys to version control
- Rotate keys periodically
- Each device has its own unique key
- Keys are required to be active (STATUS_ACTIVE)

## Troubleshooting

### 401 Unauthorized
- Check if API key is correct
- Ensure device exists and is active

### 403 Forbidden
- Device status is not "active"
- Check device status in admin panel

### Connection Refused
- Ensure FastAPI server is running on port 8001
- Check firewall settings

### Data Not Appearing
- Check if readings were sent successfully (201 response)
- Verify device in admin panel
- Check Django database directly

## Performance Considerations

- Readings are stored with index on (device, timestamp) for fast queries
- Optimal for sending data every 2000ms as specified
- Suitable for hundreds of devices with frequent updates
- For very high volume, consider archiving old data
