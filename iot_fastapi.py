"""
FastAPI application for receiving IoT sensor data.
Runs on a separate port alongside Django.
"""
import os
import sys
import django
from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, Header, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_config.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import IoTDevice, SensorReading

# Thread pool for running sync Django ORM queries
executor = ThreadPoolExecutor(max_workers=5)

# Initialize FastAPI app
app = FastAPI(
    title="IoT Data API",
    description="FastAPI endpoint for receiving IoT sensor data",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Alert thresholds — readings are only persisted when ANY threshold is crossed
ALERT_TEMP_THRESHOLD = 50.0   # °C
ALERT_GAS_THRESHOLD = 300.0   # sensor units


def is_high_alert(temperature: float, gas_level: float) -> bool:
    """Return True if any sensor reading exceeds its alert threshold."""
    return temperature > ALERT_TEMP_THRESHOLD or gas_level > ALERT_GAS_THRESHOLD


# Pydantic models for request/response
class SensorDataRequest(BaseModel):
    temperature: float
    humidity: float
    gas_level: float


class SensorDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    device_id: str
    temperature: float
    humidity: float
    gas_level: float
    timestamp: str


class DeviceStatusResponse(BaseModel):
    device_id: str
    name: str
    status: str
    last_reading: Optional[str]


# Helper function to verify API key (pure sync function)
def _sync_verify_api_key(api_key: str) -> IoTDevice:
    """Verify and retrieve IoT device by API key (sync version)."""
    try:
        device = IoTDevice.objects.get(api_key=api_key)
        if device.status != IoTDevice.STATUS_ACTIVE:
            raise ValueError("Device is not active")
        return device
    except IoTDevice.DoesNotExist:
        raise ValueError("Invalid API key")


async def verify_api_key(api_key: str) -> IoTDevice:
    """Verify and retrieve IoT device by API key (async wrapper)."""
    loop = __import__("asyncio").get_event_loop()
    try:
        return await loop.run_in_executor(executor, _sync_verify_api_key, api_key)
    except ValueError as e:
        if "Invalid API key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Device is not active",
            )


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint."""
    return {
        "message": "IoT Data API",
        "docs": "/docs",
        "status": "running",
    }


@app.post(
    "/api/v1/sensor/reading",
    status_code=status.HTTP_201_CREATED,
    tags=["Sensor"],
)
async def submit_sensor_reading(
    data: SensorDataRequest,
    response: Response,
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> Any:
    """
    Submit sensor reading data from IoT device.
    
    **Headers:**
    - `X-API-Key`: Your device API key (required)
    
    **Body:**
    - `temperature`: Temperature in Celsius (float)
    - `humidity`: Humidity in percentage (float)
    - `gas_level`: Gas sensor reading (float)
    
    **Example:**
    ```
    curl -X POST http://localhost:8001/api/v1/sensor/reading \
      -H "X-API-Key: your-device-api-key" \
      -H "Content-Type: application/json" \
      -d '{
        "temperature": 22.5,
        "humidity": 45.3,
        "gas_level": 150.0
      }'
    ```
    """
    device = await verify_api_key(x_api_key)

    # Only persist readings that cross an alert threshold
    if not is_high_alert(data.temperature, data.gas_level):
        response.status_code = status.HTTP_200_OK
        return {
            "saved": False,
            "detail": "Reading below alert threshold — not stored.",
            "temperature": data.temperature,
            "humidity": data.humidity,
            "gas_level": data.gas_level,
        }

    # Create sensor reading in a thread pool
    def _create_reading():
        reading = SensorReading.objects.create(
            device=device,
            temperature=data.temperature,
            humidity=data.humidity,
            gas_level=data.gas_level,
        )
        device.last_reading = datetime.now()
        device.save(update_fields=["last_reading"])
        return reading

    loop = __import__("asyncio").get_event_loop()
    reading = await loop.run_in_executor(executor, _create_reading)

    return {
        "id": reading.id,
        "device_id": device.device_id,
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "gas_level": reading.gas_level,
        "timestamp": reading.timestamp.isoformat(),
    }


@app.get(
    "/api/v1/device/status",
    response_model=DeviceStatusResponse,
    tags=["Device"],
)
async def get_device_status(x_api_key: str = Header(..., alias="X-API-Key")):
    """
    Get device status and last reading information.
    
    **Headers:**
    - `X-API-Key`: Your device API key (required)
    """
    device = await verify_api_key(x_api_key)
    
    return {
        "device_id": device.device_id,
        "name": device.name,
        "status": device.status,
        "last_reading": device.last_reading.isoformat() if device.last_reading else None,
    }


@app.get(
    "/api/v1/device/readings",
    tags=["Sensor"],
)
async def get_device_readings(
    x_api_key: str = Header(..., alias="X-API-Key"),
    limit: int = 10,
):
    """
    Get last N readings for the device.
    
    **Headers:**
    - `X-API-Key`: Your device API key (required)
    
    **Query Parameters:**
    - `limit`: Number of readings to return (default: 10, max: 100)
    """
    device = await verify_api_key(x_api_key)
    limit = min(limit, 100)  # Cap at 100 readings
    
    def _get_readings():
        return list(device.readings.all()[:limit])
    
    loop = __import__("asyncio").get_event_loop()
    readings = await loop.run_in_executor(executor, _get_readings)
    
    return {
        "device_id": device.device_id,
        "count": len(readings),
        "readings": [
            {
                "id": r.id,
                "temperature": r.temperature,
                "humidity": r.humidity,
                "gas_level": r.gas_level,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in readings
        ],
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
    )
