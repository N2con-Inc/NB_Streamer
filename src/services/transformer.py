"""Event transformation service for NB_Streamer with multi-tenancy support."""

import logging
from typing import Any, Dict, Optional

from ..config import config
from ..models.gelf import GELFMessage
from ..models.netbird import NetbirdEvent

logger = logging.getLogger(__name__)


class TransformerService:
    """Handle transformation of Netbird events to GELF messages with tenant context."""

    def __init__(self):
        # Use dynamic tenant resolution for multi-tenant mode
        pass

    def get_tenant_host_identifier(self, tenant_id: str) -> str:
        """Get the host identifier for a specific tenant."""
        return f"nb_streamer_{tenant_id}"

    async def transform_event(self, raw_event_data: Dict[str, Any], tenant_override: Optional[str] = None) -> GELFMessage:
        """
        Transform raw Netbird event data to GELF message with tenant context.

        Args:
            raw_event_data: Raw JSON data from Netbird
            tenant_override: Override tenant for transformation (used in multi-tenant routing)

        Returns:
            GELFMessage: Transformed GELF message ready for transmission
        """
        try:
            # Determine tenant for this event
            tenant_id = tenant_override
            if not tenant_id:
                # Use tenant from path parameter
                tenant_id = raw_event_data.get("NB_Tenant") or config.tenant_id

            # Parse the Netbird event using our flexible model
            netbird_event = NetbirdEvent.from_raw_json(raw_event_data)

            # Get tenant-specific host identifier
            host_identifier = self.get_tenant_host_identifier(tenant_id)

            # Convert to GELF message with tenant context
            gelf_message = GELFMessage.from_netbird_event(
                event_data=netbird_event.dict(),
                host=host_identifier,
                tenant_id=tenant_id,
            )

            return gelf_message

        except Exception as e:
            logger.error(f"Error transforming event for tenant {tenant_id}: {e}")
            logger.debug(f"Raw event data: {raw_event_data}")

            # Create a fallback GELF message for failed transformations
            # Determine fallback tenant
            fallback_tenant = tenant_override or raw_event_data.get("NB_Tenant") or config.tenant_id
            host_identifier = self.get_tenant_host_identifier(fallback_tenant)
            
            # Try using regular transformation but with fallback short message
            fallback_message = GELFMessage.from_netbird_event(
                event_data=raw_event_data,
                host=host_identifier,
                tenant_id=fallback_tenant,
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
            "NB_Tenant",  # Add tenant field to interesting fields
        ]

        found_fields = [
            field for field in interesting_fields if field in raw_event_data
        ]
        if found_fields:
            tenant_info = f"tenant={raw_event_data.get('NB_Tenant', 'unknown')}"
            logger.info(f"Event contains known fields: {found_fields} | {tenant_info}")

        # Log all fields for discovery
        all_fields = list(raw_event_data.keys())
        tenant_info = f"tenant={raw_event_data.get('NB_Tenant', 'unknown')}"
        logger.debug(f"All event fields: {all_fields} | {tenant_info}")

        return True
