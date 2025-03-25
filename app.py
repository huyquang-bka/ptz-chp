from fastapi import FastAPI, File, UploadFile, HTTPException
import os
from main_app.service.preset_service import PresetService
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel

app = FastAPI()
preset_service = PresetService()

# Configure upload folder for images
UPLOAD_FOLDER = 'resources/images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


class PresetData(BaseModel):
    name: str
    position: Optional[Dict[str, Any]] = None


@app.get("/api/presets/{camera_id}")
async def get_presets(camera_id: int):
    """Get all presets for a specific camera"""
    try:
        presets = preset_service.get_presets(camera_id)
        return presets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/presets/{camera_id}")
async def save_preset(camera_id: int, data: PresetData):
    """Save a new preset for a specific camera"""
    try:
        # Save preset
        preset_token = preset_service.save_preset(
            camera_id,
            data.name,
            data.position
        )

        if preset_token:
            return {
                "message": "Preset saved successfully",
                "token": preset_token
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to save preset")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/presets/{camera_id}/{preset_token}")
async def delete_preset(camera_id: int, preset_token: str):
    """Delete a specific preset"""
    try:
        success = preset_service.delete_preset(camera_id, preset_token)
        if success:
            return {"message": "Preset deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Preset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/presets/{camera_id}/{preset_token}")
async def update_preset(camera_id: int, preset_token: str, data: PresetData):
    """Update a specific preset"""
    try:
        success = preset_service.update_preset(
            camera_id,
            preset_token,
            preset_name=data.name,
            position=data.position
        )

        if success:
            return {"message": "Preset updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Preset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/save-image")
async def save_image(file: bytes = File(...)):
    """Save an image file with auto-generated name"""
    try:
        # Generate unique filename using timestamp and UUID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Save the file
        with open(filepath, 'wb') as f:
            f.write(file)

        return {
            "message": "Image saved successfully",
            "filename": filename,
            "path": filepath
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6299)
