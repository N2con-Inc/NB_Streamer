"""GELF message models for Graylog integration."""

import json
import re
import time
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, Field, field_validator


def parse_ip_port(addr_string: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse IP:port combinations and return separate IP and port.

    Handles both IPv4 and IPv6 addresses with ports.

    Args:
        addr_string: String in format "IP:port" or "[IPv6]:port"

    Returns:
        Tuple of (ip, port) or (original_string, None) if not parseable
    """
    if not isinstance(addr_string, str):
        return str(addr_string), None

    # IPv6 with port: [2001:db8::1]:8080
    ipv6_port_pattern = r"^\[([^\]]+)\]:(\d+)$"
    match = re.match(ipv6_port_pattern, addr_string)
    if match:
        return match.group(1), match.group(2)

    # IPv4 with port: 192.168.1.1:8080
    ipv4_port_pattern = r"^([^:]+):(\d+)$"
    match = re.match(ipv4_port_pattern, addr_string)
    if match:
        ip_part = match.group(1)
        port_part = match.group(2)

        # Validate it looks like an IPv4 address (basic check)
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip_part):
            return ip_part, port_part

    # If no port found or doesn't match expected patterns, return as-is
    return addr_string, None


def enhance_address_fields(flattened_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance flattened data by parsing IP:port combinations into separate fields.

    Looks for common address field patterns and splits them into IP and port components.

    Args:
        flattened_data: Already flattened dictionary

    Returns:
        Enhanced dictionary with parsed IP and port fields
    """
    enhanced_data = flattened_data.copy()

    # Common field patterns that might contain IP:port combinations
    address_field_patterns = [
        "source_addr",
        "destination_addr",
        "dest_addr",
        "src_addr",
        "remote_addr",
        "local_addr",
        "peer_addr",
        "client_addr",
        "server_addr",
    ]

    # Find and process address fields
    for field_name, field_value in list(flattened_data.items()):
        # Check if this field matches any address pattern
        field_lower = field_name.lower()
        is_address_field = any(
            pattern in field_lower for pattern in address_field_patterns
        )

        if is_address_field and isinstance(field_value, str):
            ip, port = parse_ip_port(field_value)

            if port is not None:
                # Replace the original field with just the IP
                enhanced_data[field_name] = ip

                # Add a new port field
                # Convert source_addr -> source_port, destination_addr -> port
                port_field_name = field_name.replace("_addr", "_port").replace(
                    "_address", "_port"
                )
                if (
                    port_field_name == field_name
                ):  # If no replacement happened, append _port
                    port_field_name = f"{field_name}_port"

                enhanced_data[port_field_name] = port

    return enhanced_data


def flatten_dict(
    data: Dict[str, Any], parent_key: str = "", separator: str = "_"
) -> Dict[str, Any]:
    """
    Recursively flatten a nested dictionary.

    Args:
        data: Dictionary to flatten
        parent_key: Current parent key path
        separator: Separator to use between keys

    Returns:
        Flattened dictionary with concatenated keys
    """
    items = []

    for key, value in data.items():
        # Create new key with parent path
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            # Recursively flatten nested dictionaries
            items.extend(flatten_dict(value, new_key, separator).items())
        elif isinstance(value, list):
            # Handle lists by creating indexed fields or converting to JSON
            if len(value) > 0 and all(isinstance(item, dict) for item in value):
                # If list contains dictionaries, flatten each with index
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        indexed_key = f"{new_key}_{i}"
                        items.extend(flatten_dict(item, indexed_key, separator).items())
                    else:
                        items.append((f"{new_key}_{i}", str(item)))
            else:
                # For simple lists or mixed types, convert to JSON string
                items.append((new_key, json.dumps(value)))
        elif isinstance(value, datetime):
            # Convert datetime to ISO string
            items.append((new_key, value.isoformat()))
        elif value is None:
            # Skip None values
            continue
        else:
            # Keep primitive values as-is, but convert to string for safety
            items.append((new_key, str(value)))

    return dict(items)


class GELFMessage(BaseModel):
    """
    GELF (Graylog Extended Log Format) message structure.

    Based on GELF specification: https://docs.graylog.org/docs/gelf
    """

    # Required GELF fields
    version: str = Field(default="1.1", description="GELF spec version")
    host: str = Field(..., description="Source host")
    short_message: str = Field(..., description="Short descriptive message")

    # Optional GELF fields
    full_message: Optional[str] = Field(None, description="Long message")
    timestamp: Optional[float] = Field(None, description="Unix timestamp")
    level: Optional[int] = Field(6, description="Syslog level (default: INFO)")
    facility: Optional[str] = Field("nb_streamer", description="Log facility")

    # Custom fields (must be prefixed with _)
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict, description="Custom GELF fields"
    )

    @field_validator("timestamp", mode="before")
    @classmethod
    def set_timestamp(cls, v):
        """Set timestamp to current time if not provided."""
        if v is None:
            return time.time()
        if isinstance(v, datetime):
            return v.timestamp()
        return v

    @field_validator("custom_fields")
    @classmethod
    def validate_custom_fields(cls, v):
        """Ensure all custom fields are prefixed with underscore."""
        validated = {}
        for key, value in v.items():
            if not key.startswith("_"):
                key = f"_{key}"
            validated[key] = value
        return validated

    def model_dump_dict(self, **kwargs) -> Dict[str, Any]:
        """Convert to dictionary with custom fields flattened."""
        data = self.model_dump(exclude={"custom_fields"}, **kwargs)

        # Add custom fields at top level
        if self.custom_fields:
            data.update(self.custom_fields)

        # Remove None values
        return {k: v for k, v in data.items() if v is not None}

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Backward compatibility method."""
        return self.model_dump_dict(**kwargs)

    def to_json(self) -> str:
        """Convert to JSON string for transmission."""
        return json.dumps(self.dict(), separators=(",", ":"))

    @classmethod
    def from_netbird_event(
        cls,
        event_data: Dict[str, Any],
        host: str,
        tenant_id: str,
        short_message: Optional[str] = None,
    ) -> "GELFMessage":
        """
        Create GELF message from Netbird event data with flattened and enhanced fields.

        Args:
            event_data: Netbird event data dictionary
            host: Source host identifier
            tenant_id: Tenant/client identifier
            short_message: Override for short message
        """
        # Generate short message if not provided
        if not short_message:
            # Try to use the actual Message field from Netbird events
            if "Message" in event_data and event_data["Message"]:
                short_message = str(event_data["Message"]).strip()
            else:
                # Fallback to constructing from available fields
                event_type = event_data.get("type", event_data.get("event_type", ""))
                action = event_data.get("action", "")
                user = event_data.get("user", event_data.get("InitiatorID", ""))

                if action and user:
                    short_message = f"Netbird {event_type}: {action} by {user}"
                elif event_type:
                    short_message = f"Netbird {event_type}"
                elif user:
                    short_message = f"Netbird event by {user}"
                else:
                    short_message = "Netbird event"

        # Handle timestamp - intelligently choose between timestamp fields
        timestamp = None

        # Try Timestamp field first (capitalized) as it contains timestamp
        timestamp_field = event_data.get("Timestamp")
        lowercase_timestamp_field = event_data.get("timestamp")

        # Function to validate if a value looks like a timestamp
        def is_valid_timestamp_value(value):
            if isinstance(value, (int, float)):
                return True
            if isinstance(value, str):
                # Check if it looks like an ISO timestamp
                return (
                    "T" in value and (":" in value or "Z" in value)
                ) or value.replace(".", "").replace("-", "").isdigit()
            return False

        # Choose the field that actually contains timestamp data
        chosen_ts_field = None
        chosen_ts_field_key = None
        if timestamp_field and is_valid_timestamp_value(timestamp_field):
            chosen_ts_field_key = "Timestamp"
            chosen_ts_field = timestamp_field
        elif lowercase_timestamp_field and is_valid_timestamp_value(
            lowercase_timestamp_field
        ):
            chosen_ts_field_key = "timestamp"
            chosen_ts_field = lowercase_timestamp_field

        if chosen_ts_field:
            if isinstance(chosen_ts_field, str):
                try:
                    # Try parsing ISO format
                    dt = datetime.fromisoformat(chosen_ts_field.replace("Z", "+00:00"))
                    timestamp = dt.timestamp()
                except ValueError:
                    # If parsing fails, use current time
                    timestamp = time.time()
            elif isinstance(chosen_ts_field, (int, float)):
                timestamp = chosen_ts_field
            elif isinstance(chosen_ts_field, datetime):
                timestamp = chosen_ts_field.timestamp()

        # If no valid timestamp found, use current time
        if timestamp is None:
            timestamp = time.time()

        # Convert level to syslog level if it's a string
        level = 6  # Default INFO
        if "level" in event_data:
            level_str = str(event_data["level"]).upper()
            level_mapping = {
                "EMERGENCY": 0,
                "EMERG": 0,
                "ALERT": 1,
                "CRITICAL": 2,
                "CRIT": 2,
                "ERROR": 3,
                "ERR": 3,
                "WARNING": 4,
                "WARN": 4,
                "NOTICE": 5,
                "INFO": 6,
                "INFORMATION": 6,
                "DEBUG": 7,
            }
            level = level_mapping.get(level_str, 6)

        # Prepare custom fields with flattened and enhanced structure
        custom_fields = {}

        # Add tenant field
        custom_fields["_NB_tenant"] = tenant_id

        # Flatten the entire event data structure
        flattened_data = flatten_dict(event_data)

        # Enhance flattened data by parsing IP:port combinations
        enhanced_data = enhance_address_fields(flattened_data)

        # Add all enhanced fields with NB_ prefix
        for key, value in enhanced_data.items():
            # Skip timestamp and level fields that are used for standard GELF fields
            # But preserve timestamp fields with non-timestamp data as custom
            skip_field = False
            if key in ["level", "Timestamp"]:
                skip_field = True
            elif key == "timestamp":
                # Only skip if this was the field we used for the GELF timestamp
                if chosen_ts_field_key == key:
                    skip_field = True

            if not skip_field:
                # Ensure we have a string value for GELF
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                elif not isinstance(value, str):
                    value = str(value)

                custom_fields[f"_NB_{key}"] = value

        # Keep original event data for full_message (for debugging/reference)
        serializable_event_data = {}
        for key, value in event_data.items():
            if isinstance(value, datetime):
                serializable_event_data[key] = value.isoformat()
            elif isinstance(value, (dict, list)):
                serializable_event_data[key] = value
            else:
                serializable_event_data[key] = value

        return cls(
            host=host,
            short_message=short_message,
            full_message=json.dumps(serializable_event_data, indent=2),
            timestamp=timestamp,
            level=level,
            custom_fields=custom_fields,
        )
