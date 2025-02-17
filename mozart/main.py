from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import redis
import json
import threading
import time
import os

app = FastAPI()

# Connect to Redis (ensure Redis is running)
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

# In-memory config storage
CONFIG_STORAGE: Dict[str, dict] = {
    "latest": {"version": "1.0.0", "data": {"settingA": "valueA", "settingB": "valueB"}}
}

class ConfigUpdate(BaseModel):
    version: str
    data: dict

@app.get("/config/latest")
def get_latest_config():
    return CONFIG_STORAGE["latest"]

@app.post("/config/update")
def update_config(config: ConfigUpdate):
    CONFIG_STORAGE[config.version] = {"version": config.version, "data": config.data}
    CONFIG_STORAGE["latest"] = CONFIG_STORAGE[config.version]
    
    # Publish update event to Redis Pub/Sub
    redis_client.publish("config_updates", json.dumps({"version": config.version}))
    
    return {"message": "Config updated", "version": config.version}

# Sidecar Agent to listen for updates
def sidecar_agent():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("config_updates")
    
    print("Sidecar Agent started, listening for config updates...")
    
    for message in pubsub.listen():
        if message["type"] == "message":
            version_info = json.loads(message["data"])
            print(f"New config version received: {version_info['version']}")
            latest_config = redis_client.get("config_latest")
            if latest_config:
                with open("/shared/config.json", "w") as f:
                    f.write(latest_config)
                print("Config written to shared volume.")

# Fake Application Pod
def fake_application():
    while True:
        if os.path.exists("/shared/config.json"):
            with open("/shared/config.json", "r") as f:
                config = f.read()
            print(f"Fake App loaded config: {config}")
        time.sleep(5)

# Start Sidecar Agent in a separate thread
threading.Thread(target=sidecar_agent, daemon=True).start()

# Start Fake Application Pod in a separate thread
threading.Thread(target=fake_application, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


ChatGPT is generating a response...