"""Configuration management for NB_Streamer."""

from typing import Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Server Configuration
    nb_host: str = Field(default="0.0.0.0")
    nb_port: int = Field(default=8000)
    nb_debug: bool = Field(default=False)

    # Graylog Configuration
    nb_graylog_host: str
    nb_graylog_port: int = Field(default=12201)
    nb_graylog_protocol: Literal["udp", "tcp"] = Field(default="udp")

    # Tenant/Client Configuration
    nb_tenant_id: str

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

    # Logging Configuration
    nb_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")

    # Properties for backward compatibility
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
    def graylog_host(self) -> str:
        return self.nb_graylog_host

    @property
    def graylog_port(self) -> int:
        return self.nb_graylog_port

    @property
    def graylog_protocol(self) -> Literal["udp", "tcp"]:
        return self.nb_graylog_protocol

    @property
    def tenant_id(self) -> str:
        return self.nb_tenant_id

    @property
    def auth_type(self) -> Literal["none", "bearer", "basic", "header"]:
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
    def log_level(self) -> Literal["DEBUG", "INFO", "WARNING", "ERROR"]:
        return self.nb_log_level

    @field_validator("nb_auth_token")
    @classmethod
    def validate_bearer_auth(cls, v, info):
        """Validate bearer token is provided when auth_type is bearer."""
        if info.data.get("nb_auth_type") == "bearer" and not v:
            raise ValueError("nb_auth_token is required when nb_auth_type is 'bearer'")
        return v

    @field_validator("nb_auth_username")
    @classmethod
    def validate_basic_auth_username(cls, v, info):
        """Validate username is provided when auth_type is basic."""
        if info.data.get("nb_auth_type") == "basic" and not v:
            raise ValueError(
                "nb_auth_username is required when nb_auth_type is 'basic'"
            )
        return v

    @field_validator("nb_auth_password")
    @classmethod
    def validate_basic_auth_password(cls, v, info):
        """Validate password is provided when auth_type is basic."""
        if info.data.get("nb_auth_type") == "basic" and not v:
            raise ValueError(
                "nb_auth_password is required when nb_auth_type is 'basic'"
            )
        return v

    @field_validator("nb_auth_header_name")
    @classmethod
    def validate_header_auth_name(cls, v, info):
        """Validate header name is provided when auth_type is header."""
        if info.data.get("nb_auth_type") == "header" and not v:
            raise ValueError(
                "nb_auth_header_name is required when nb_auth_type is 'header'"
            )
        return v

    @field_validator("nb_auth_header_value")
    @classmethod
    def validate_header_auth_value(cls, v, info):
        """Validate header value is provided when auth_type is header."""
        if info.data.get("nb_auth_type") == "header" and not v:
            raise ValueError(
                "nb_auth_header_value is required when nb_auth_type is 'header'"
            )
        return v

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


# Global config instance
config = Config()
