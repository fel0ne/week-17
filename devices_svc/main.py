from fastapi import FastAPI
import requests
from pydantic import BaseModel

app = FastAPI(title="Devices Service")

class DeviceSchema(BaseModel):
    name: str
    serial: str
    owner_id: int

@app.post("/api/devices")
def create_device(device: DeviceSchema):
    # созданиe устройства...
    
    # cервер девайсов уведомляет сервис нотификаций
    try:
        requests.post("http://notifications-svc-s05:8151/api/notifications", json={
            "user_id": device.owner_id,
            "title": "New Device Registered",
            "body": f"Device {device.name} (S/N: {device.serial}) added.",
            "channel": "email" 
        })
    except Exception as e:

        print(f"Notification failed but device created: {e}")
        return {"status": "Device created, notification queued/failed", "device": device}

    return {"status": "Device created and user notified", "device": device}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8266)