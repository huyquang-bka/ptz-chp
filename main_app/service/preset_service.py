import json
import os
from typing import Dict, List, Any
import uuid


class PresetService:
    """Service for managing camera presets stored in a JSON file"""

    def __init__(self, preset_file_path="resources/database/preset.json"):
        self.preset_file_path = preset_file_path
        self._ensure_preset_file_exists()

    def _ensure_preset_file_exists(self):
        """Ensure the preset file exists, create it if it doesn't"""
        os.makedirs(os.path.dirname(self.preset_file_path), exist_ok=True)
        if not os.path.exists(self.preset_file_path):
            with open(self.preset_file_path, 'w') as f:
                json.dump({}, f)

    def _load_presets(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load presets from the JSON file"""
        try:
            with open(self.preset_file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_presets(self, presets: Dict[str, List[Dict[str, Any]]]):
        """Save presets to the JSON file"""
        with open(self.preset_file_path, 'w') as f:
            json.dump(presets, f, indent=2)

    def get_presets(self, camera_id: int) -> List[Dict[str, Any]]:
        """Get presets for a specific camera"""
        presets = self._load_presets()
        return presets.get(str(camera_id), [])

    def save_preset(self, camera_id: int, preset_name: str, position: Dict[str, Any] = None) -> str:
        """Save a preset for a specific camera"""
        presets = self._load_presets()
        camera_id_str = str(camera_id)

        if camera_id_str not in presets:
            presets[camera_id_str] = []

        # Generate a unique token for the preset
        preset_token = str(uuid.uuid4())

        # Create preset object
        preset = {
            "token": preset_token,
            "Name": preset_name,
            "position": position or {}
        }

        # Add to presets
        presets[camera_id_str].append(preset)

        # Save to file
        self._save_presets(presets)

        return preset_token

    def update_preset(self, camera_id: int, preset_token: str, preset_name: str = None, position: Dict[str, Any] = None) -> bool:
        """Update a preset for a specific camera"""
        presets = self._load_presets()
        camera_id_str = str(camera_id)

        if camera_id_str not in presets:
            return False

        # Find the preset
        for preset in presets[camera_id_str]:
            if preset["token"] == preset_token:
                # Update name if provided
                if preset_name is not None:
                    preset["Name"] = preset_name

                # Update position if provided
                if position is not None:
                    preset["position"] = position

                # Save to file
                self._save_presets(presets)
                return True

        return False

    def delete_preset(self, camera_id: int, preset_token: str) -> bool:
        """Delete a preset for a specific camera"""
        presets = self._load_presets()
        camera_id_str = str(camera_id)

        if camera_id_str not in presets:
            return False

        # Find and remove the preset
        for i, preset in enumerate(presets[camera_id_str]):
            if preset["token"] == preset_token:
                presets[camera_id_str].pop(i)
                # Save to file
                self._save_presets(presets)
                return True

        return False
