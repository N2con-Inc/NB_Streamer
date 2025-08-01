"""Event transformation service for NB_Streamer."""

import logging
from typing import Any, Dict

from ..config import config
from ..models.gelf import GELFMessage
from ..models.netbird import NetbirdEvent

logger = logging.getLogger(__name__)


class TransformerService:
    """Handle transformation of Netbird events to GELF messages."""

    def __init__(self):
        self.tenant_id = config.tenant_id
        self.host_identifier = f"nb_streamer_{config.tenant_id}"

    async def transform_event(self, raw_event_data: Dict[str, Any]) -> GELFMessage:
        """
        Transform raw Netbird event data to GELF message.

        Args:
            raw_event_data: Raw JSON data from Netbird

        Returns:
            GELFMessage: Transformed GELF message ready for transmission
        """
        try:
            # Parse the Netbird event using our flexible model
            netbird_event = NetbirdEvent.from_raw_json(raw_event_data)

            # Convert to GELF message
            gelf_message = GELFMessage.from_netbird_event(
                event_data=netbird_event.dict(),
                host=self.host_identifier,
                tenant_id=self.tenant_id,
            )

            return gelf_message

        except Exception as e:
            logger.error(f"Error transforming event: {e}")
            logger.debug(f"Raw event data: {raw_event_data}")

            # Create a fallback GELF message for failed transformations
            # Try using regular transformation but with fallback short message
            fallback_message = GELFMessage.from_netbird_event(
                event_data=raw_event_data,
                host=self.host_identifier,
                tenant_id=self.tenant_id,
                short_message=f"Event transformation had issues: {str(e)}",
            )

            # Add error information to custom fields
            fallback_message.custom_fields["_NB_transformation_error"] = str(e)
            fallback_message.custom_fields["_NB_transformation_failed"] = True

            return fallback_message

    def validate_event_structure(self, raw_event_data: Dict[str, Any]) -> bool:
        """
        Validate basic event structure.

        This is useful for understanding what Netbird is actually sending
        and can be extended as we learn more about the event structure.

        Args:
            raw_event_data: Raw JSON data from Netbird

        Returns:
            bool: True if basic validation passes
        """
        if not isinstance(raw_event_data, dict):
            logger.warning("Event data is not a dictionary")
            return False

        if not raw_event_data:
            logger.warning("Event data is empty")
            return False

        # Log interesting fields we discover
        interesting_fields = [
            "type",
            "event_type",
            "timestamp",
            "user",
            "peer",
            "network",
            "action",
            "level",
            "message",
            "id",
            "source",
        ]

        found_fields = [
            field for field in interesting_fields if field in raw_event_data
        ]
        if found_fields:
            logger.info(f"Event contains known fields: {found_fields}")

        # Log all fields for discovery
        all_fields = list(raw_event_data.keys())
        logger.debug(f"All event fields: {all_fields}")

        return True
