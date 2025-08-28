"""Graylog service for NB_Streamer."""

import socket
import zlib

from ..config import config
from ..models.gelf import GELFMessage


class GraylogService:
    """Handle sending GELF messages to Graylog."""

    def __init__(self):
        # Create socket for UDP or TCP communication
        self.sock = socket.socket(
            socket.AF_INET,
            (
                socket.SOCK_DGRAM
                if config.graylog_protocol == "udp"
                else socket.SOCK_STREAM
            ),
        )

    def connect(self):
        """Establish connection in case of TCP protocol."""
        if config.graylog_protocol == "tcp":
            self.sock.connect((config.graylog_host, config.graylog_port))

    def send_gelf_message(self, message: GELFMessage):
        """
        Send a GELF message to Graylog using configured protocol.

        Args:
            message: GELFMessage object to be sent
        """
        # Convert the message to JSON
        message_json = message.to_json().encode("utf-8")

        # Compress if needed
        if config.compression_enabled:
            message_json = zlib.compress(message_json)

        # Send the message
        self.sock.sendto(message_json, (config.graylog_host, config.graylog_port))

    def close(self):
        """Close the socket connection."""
        self.sock.close()

    async def forward_event(self, transformed_event: dict) -> bool:
        """
        Forward an event to Graylog.
        
        Args:
            transformed_event: Dictionary containing the transformed event data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create GELF message from transformed event
            from ..models.gelf import GELFMessage
            gelf_message = transformed_event
            
            # Connect if using TCP
            self.connect()
            
            # Send the message
            self.send_gelf_message(gelf_message)
            
            return True
        except Exception as e:
            # Log the error but don't raise - return False to indicate failure
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to forward event to Graylog: {str(e)}")
            return False
        finally:
            # Always close connection for TCP
            if config.graylog_protocol == "tcp":
                try:
                    self.close()
                except:
                    pass
