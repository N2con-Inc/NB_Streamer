"""
Configuration management for NB_Streamer using Pydantic.
Handles environment variables, validation, and default values.
"""

import logging
import os
from pathlib import Path
from typing import Optional, Set, Literal

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict


logger = logging.getLogger(__name__)


class Config(BaseSettings):
    """Configuration class with environment variable support and validation."""
    
    # Version and basic settings
    version: str = "0.3.1"
    
    # Server Configuration
    nb_host: str = Field(default="0.0.0.0")
    nb_port: int = Field(default=8000)  
    nb_debug: bool = Field(default=False)
    nb_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")

    # Graylog Configuration
    nb_graylog_host: str = Field(default="localhost")
    nb_graylog_port: int = Field(default=12201)
    nb_graylog_protocol: Literal["tcp", "udp"] = Field(default="udp")
    nb_graylog_timeout: int = Field(default=10)

    # Multi-tenancy Configuration
    nb_tenants: str = Field(default="")
    nb_tenants_file: Optional[str] = Field(default=None)
    nb_require_tenant_path: bool = Field(default=True)
    nb_trust_proxy_headers: bool = Field(default=True)
    nb_expose_tenants: bool = Field(default=False)

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

    model_config = SettingsConfigDict(
env_file=".env",
case_sensitive=True)

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
    def graylog_timeout(self) -> int:
        return self.nb_graylog_timeout

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

    @property
    def tenants(self) -> Set[str]:
        """Get the set of configured tenants."""
        tenants = set()
        
        # Add from environment variable
        if self.nb_tenants.strip():
            env_tenants = [t.strip().lower() for t in self.nb_tenants.split(",")]
            tenants.update(tenant for tenant in env_tenants if tenant)
        
        # Add from file if specified
        if self.nb_tenants_file:
            try:
                tenants_file = Path(self.nb_tenants_file)
                if tenants_file.exists():
                    content = tenants_file.read_text().strip()
                    file_tenants = [t.strip().lower() for t in content.split("\n")]
                    tenants.update(tenant for tenant in file_tenants if tenant and not tenant.startswith("#"))
                    logger.info(f"Loaded {len(file_tenants)} tenants from {self.nb_tenants_file}")
                else:
                    logger.warning(f"Tenants file {self.nb_tenants_file} not found")
            except Exception as e:
                logger.error(f"Error reading tenants file {self.nb_tenants_file}: {e}")
        
        return tenants

    def validate_configuration(self):
        """Validate configuration and log startup information."""
        tenant_list = list(self.tenants)
        
        if not tenant_list:
            logger.error("No tenants configured. Please set NB_TENANTS environment variable.")
            raise ValueError("At least one tenant must be configured")
        
        # Log configuration summary
        logger.info("=== NB_Streamer Configuration Summary ===")
        logger.info(f"Multi-tenancy enabled: True")
        logger.info(f"Configured tenants: {tenant_list}")
        
        if not tenant_list:
            logger.warning("No tenants configured - check your configuration")

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
