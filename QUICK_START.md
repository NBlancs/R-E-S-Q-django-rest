# Quick Start Guide - IoT Device Integration

## ✓ What's Been Set Up

Your Django backend now has a complete **IoT integration system** with:

- **FastAPI Service** for receiving real-time sensor data (temperature, humidity, gas level)
- **API Key Authentication** for device security
- **Automatic Data Storage** in Django database
- **Interactive API Docs** with Swagger UI
- **Admin Dashboard** to manage devices and view readings
- **Example Device Simulator** for testing

---

## 🚀 Quick Start (5 minutes)

### 1. Start All Services
```bash
python run_all.py
```
This starts both Django (8000) and FastAPI (8001)

### 2. Create Your First Device
```bash
python manage.py create_iot_device \
  --device-id SENSOR_001 \
  --name "My Temperature Sensor" \
  --location "Room A"
```

**Copy the generated API Key** - you'll need it!

### 3. Test with Example Device
```bash
python example_iot_device.py --api-key iot_YOUR_API_KEY_HERE
```

The simulator will send test readings every 2 seconds.

### 4. View the Data

**FastAPI Interactive Docs:**
- Open: http://localhost:8001/docs
- Test endpoints directly in the browser

**Django Admin Panel:**
- Open: http://localhost:8000/admin
- Navigate to "IoT Devices" or "Sensor Readings"
- View all recorded sensor data

---

## 📡 Real IoT Device Integration

### Using cURL
```bash
curl -X POST http://localhost:8001/api/v1/sensor/reading \
  -H "X-API-Key: iot_YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 22.5,
    "humidity": 45.3,
    "gas_level": 150.0
  }'
```

### Using Python
```python
import requests

api_key = "iot_YOUR_API_KEY"
url = "http://localhost:8001/api/v1/sensor/reading"

data = {
    "temperature": 22.5,
    "humidity": 45.3,
    "gas_level": 150.0
}

headers = {"X-API-Key": api_key}
response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `iot_fastapi.py` | FastAPI server for receiving IoT data |
| `run_all.py` | Start both Django & FastAPI |
| `example_iot_device.py` | Test device simulator |
| `api/models.py` | IoTDevice & SensorReading models |
| `IoT_SETUP.md` | Complete documentation |
| `api/management/commands/create_iot_device.py` | Device creation command |

---

## 🔑 API Key Security

⚠️ **Important:**
- Each device gets a **unique API key**
- Keys are generated securely and shown only once
- Store keys in `.env` files, not in code
- If a key is compromised, create a new device
- Only active devices can send data

---

## 📊 Database Structure

### IoTDevice
- `device_id` - Unique identifier for your device
- `name` - Friendly name
- `location` - Physical location
- `api_key` - Secure authentication key
- `status` - active/inactive/maintenance
- `last_reading` - Timestamp of last data received

### SensorReading
- `device` - Link to IoTDevice
- `temperature` - In Celsius
- `humidity` - In percentage
- `gas_level` - Sensor value
- `timestamp` - When data was received

---

## 🛠️ Useful Commands

**Create new device:**
```bash
python manage.py create_iot_device --device-id DEVICE_002 --name "Sensor 2" --location "Room B"
```

**Django shell to query data:**
```bash
python manage.py shell
# Then:
from api.models import IoTDevice, SensorReading
device = IoTDevice.objects.get(device_id='SENSOR_001')
readings = device.readings.all()[:10]  # Latest 10
```

**Run tests:**
```bash
python manage.py test
```

---

## ✅ Test Device (Pre-created)

Device ID: `TEST_DEVICE_001`
API Key: `iot_H9U0OgAO2lu2FgL3ieCCmsGaG3csEzLzX7XHX2M0cdQ`
Location: Lab

Use this to test the system before creating your own devices.

---

## 📚 API Endpoints Summary

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/v1/sensor/reading` | POST | API Key | Submit sensor reading |
| `/api/v1/device/status` | GET | API Key | Get device status |
| `/api/v1/device/readings` | GET | API Key | Get historical data |
| `/health` | GET | None | Health check |
| `/docs` | GET | None | API documentation |

---

## 🎯 Next Steps

1. **Run the system:** `python run_all.py`
2. **Create your devices:** `python manage.py create_iot_device ...`
3. **Send test data:** `python example_iot_device.py --api-key ...`
4. **View in admin:** http://localhost:8000/admin
5. **Check API docs:** http://localhost:8001/docs
6. **Read full guide:** See `IoT_SETUP.md`

---

## ❓ Troubleshooting

**Port already in use:**
- Change port in `iot_fastapi.py` line 199
- Or: `netstat -ano | find "8001"` to find process

**API Key invalid (401):**
- Check key spelling
- Verify device exists in admin
- Device must have status "active"

**Connection refused:**
- Make sure `run_all.py` is running
- Check firewall settings

**Missing dependencies:**
- Run: `pip install -r requirements.txt`

---

For complete documentation, see **IoT_SETUP.md**
