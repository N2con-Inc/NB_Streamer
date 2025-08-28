"""
Configuration management for NB_Streamer using Pydantic.
Handles environment variables, validation, and default values.
"""

import logging
import os
from pathlib import Path
from typing import Optional, Set, Literal, List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


logger = logging.getLogger(__name__)


class Config(BaseSettings):
    """Configuration class with environment variable support and validation."""
    
    # Version and basic settings
    version: str = "0.3.2"
    
    # Server Configuration
    nb_host: str = Field(default="0.0.0.0")
    nb_port: int = Field(default=8080)  # Fixed default port
    nb_debug: bool = Field(default=False)
    nb_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")

    # Graylog Configuration
    nb_graylog_host: str = Field(default="localhost")
    nb_graylog_port: int = Field(default=12201)
    nb_graylog_protocol: Literal["udp", "tcp"] = Field(default="udp")

    # Multi-tenant Configuration
    nb_tenants: str = Field(default="")
    nb_require_tenant_path: bool = Field(default=True)
    nb_trust_proxy_headers: bool = Field(default=True)
    nb_expose_tenants: bool = Field(default=False)

    # Legacy Support (disabled by default)
    nb_allow_legacy_events: bool = Field(default=False)

    # Authentication Configuration
    nb_auth_type: Literal["none", "bearer", "basic", "header"] = Field(default="none")
    nb_auth_token: Optional[str] = Field(default=None)
    nb_auth_username: Optional[str] = Field(default=None)
    nb_auth_password: Optional[str] = Field(default=None)
    nb_auth_header_name: Optional[str] = Field(default=None)
    nb_auth_header_value: Optional[str] = Field(default=None)

    # Message Configuration
    nb_compression_enabled: bool = Field(default=True)
    nb_max_message_size: int = Field(default=8192)

    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        # env_file=".env",  # Handled by Docker Compose
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix=""
    )

    @property
    def host(self) -> str:
        return self.nb_host

    @property
    def port(self) -> int:
        return self.nb_port

    @property
    def debug(self) -> bool:
        return self.nb_debug

    @property
    def log_level(self) -> str:
        return self.nb_log_level

    @property
    def graylog_host(self) -> str:
        return self.nb_graylog_host

    @property
    def graylog_port(self) -> int:
        return self.nb_graylog_port

    @property
    def graylog_protocol(self) -> str:
        return self.nb_graylog_protocol
    @property
    def tenants(self) -> str:
        return self.nb_tenants

    @property
    def require_tenant_path(self) -> bool:
        return self.nb_require_tenant_path

    @property
    def trust_proxy_headers(self) -> bool:
        return self.nb_trust_proxy_headers

    @property
    def expose_tenants(self) -> bool:
        return self.nb_expose_tenants

    @property
    def allow_legacy_events(self) -> bool:
        return self.nb_allow_legacy_events

    @property
    def auth_type(self) -> str:
        return self.nb_auth_type

    @property
    def auth_token(self) -> Optional[str]:
        return self.nb_auth_token

    @property
    def auth_username(self) -> Optional[str]:
        return self.nb_auth_username

    @property
    def auth_password(self) -> Optional[str]:
        return self.nb_auth_password

    @property
    def auth_header_name(self) -> Optional[str]:
        return self.nb_auth_header_name

    @property
    def auth_header_value(self) -> Optional[str]:
        return self.nb_auth_header_value

    @property
    def compression_enabled(self) -> bool:
        return self.nb_compression_enabled

    @property
    def max_message_size(self) -> int:
        return self.nb_max_message_size

    def get_tenant_list(self) -> List[str]:
        """Get list of configured tenants."""
        if not self.tenants:
            return []
        return [tenant.strip() for tenant in self.tenants.split(",") if tenant.strip()]

    def validate_startup_configuration(self) -> None:
        """Validate configuration at startup."""
        tenant_list = self.get_tenant_list()
        
        if self.require_tenant_path and not tenant_list:
            raise ValueError("NB_TENANTS must be configured when NB_REQUIRE_TENANT_PATH is True")
        
        if tenant_list:
            logger.info(f"Configured tenants: {tenant_list}")
        else:
            logger.warning("No tenants configured - check your configuration")

        # Validate authentication configuration
        if self.auth_type == "bearer" and not self.auth_token:
            raise ValueError("Bearer token is required when auth_type is bearer")
        
        if self.auth_type == "basic" and (not self.auth_username or not self.auth_password):
            raise ValueError("Username and password are required when auth_type is basic")
        
        if self.auth_type == "header" and (not self.auth_header_name or not self.auth_header_value):
            raise ValueError("Header name and value are required when auth_type is header")

    @field_validator("nb_auth_token")
    @classmethod
    def validate_bearer_auth(cls, v, info):
        """Validate bearer token is provided when auth_type is bearer."""
        if hasattr(info, 'data') and info.data.get("nb_auth_type") == "bearer" and not v:
            raise ValueError("Bearer token is required when auth_type is bearer")
        return v

    @field_validator("nb_auth_username", "nb_auth_password")
    @classmethod  
    def validate_basic_auth(cls, v, info):
        """Validate username/password are provided when auth_type is basic."""
        if hasattr(info, 'data') and info.data.get("nb_auth_type") == "basic":
            if not info.data.get("nb_auth_username") or not info.data.get("nb_auth_password"):
                raise ValueError("Username and password are required when auth_type is basic")
        return v

    @field_validator("nb_auth_header_name", "nb_auth_header_value")
    @classmethod
    def validate_header_auth(cls, v, info):
        """Validate header name/value are provided when auth_type is header."""  
        if hasattr(info, 'data') and info.data.get("nb_auth_type") == "header":
            if not info.data.get("nb_auth_header_name") or not info.data.get("nb_auth_header_value"):
                raise ValueError("Header name and value are required when auth_type is header")
        return v


# Create default configuration instance
config = Config()
