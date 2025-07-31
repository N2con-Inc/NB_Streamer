"""Netbird event models."""

from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class NetbirdEvent(BaseModel):
    """
    Flexible model for Netbird events.
    
    This model is designed to capture any JSON structure that Netbird sends,
    allowing us to discover the actual field structure during development.
    All fields are optional to handle varying event types.
    """
    
    # Common fields we expect based on typical event systems
    timestamp: Optional[datetime] = None
    event_type: Optional[str] = Field(None, alias="type")
    event_id: Optional[str] = Field(None, alias="id")
    source: Optional[str] = None
    user: Optional[str] = None
    peer: Optional[str] = None
    network: Optional[str] = None
    action: Optional[str] = None
    message: Optional[str] = None
    level: Optional[str] = None
    
    # Catch-all for any additional fields
    additional_data: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {
        "populate_by_name": True,
        "extra": "allow"  # Allow extra fields to be captured
    }
        
    def model_dump_dict(self, **kwargs) -> Dict[str, Any]:
        """
        Override model_dump method to flatten additional_data.
        
        This ensures all fields (both known and unknown) are at the top level
        when we convert to dictionary for GELF transformation.
        """
        data = self.model_dump(**kwargs)
        
        # Move additional_data fields to top level
        if "additional_data" in data:
            additional = data.pop("additional_data")
            data.update(additional)
            
        # Remove None values to keep the output clean
        return {k: v for k, v in data.items() if v is not None}
    
    def dict(self, **kwargs) -> Dict[str, Any]:
        """Backward compatibility method."""
        return self.model_dump_dict(**kwargs)
    
    @classmethod
    def from_raw_json(cls, raw_data: Dict[str, Any]) -> "NetbirdEvent":
        """
        Create NetbirdEvent from raw JSON data.
        
        This method handles the flexible parsing of unknown field structures.
        """
        # Extract known fields, handling special cases
        known_fields = {}
        known_field_keys = set()
        
        for field_name, field_info in cls.model_fields.items():
            if field_name == "additional_data":
                continue
                
            field_key = field_info.alias if field_info.alias else field_name
            known_field_keys.add(field_key)
            
            if field_key in raw_data:
                value = raw_data[field_key]
                
                # Special handling for timestamp field
                if field_name == "timestamp" and isinstance(value, str):
                    try:
                        # Parse ISO timestamp to datetime
                        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    except ValueError:
                        # If parsing fails, keep as string
                        pass
                
                known_fields[field_name] = value
        
        # Put everything else in additional_data
        additional_data = {
            k: v for k, v in raw_data.items()
            if k not in known_field_keys
        }
        
        return cls(
            **{k: v for k, v in known_fields.items() if v is not None},
            additional_data=additional_data
        )
