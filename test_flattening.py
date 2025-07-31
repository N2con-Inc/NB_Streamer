#!/usr/bin/env python3
"""Test script to demonstrate the GELF field flattening functionality."""

import json
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.gelf import GELFMessage

# Sample complex Netbird event
sample_event = {
    "ID": "flattening-demo-001",
    "Timestamp": "2025-07-31T22:45:00Z",
    "Message": "Connection established",
    "InitiatorID": "user@example.com",
    "target_id": "peer-001",
    "meta": {
        "source_addr": "10.0.1.100",
        "destination_addr": "10.0.2.200",
        "port": 22,
        "protocol": "TCP",
        "connection_info": {
            "encrypted": True,
            "cipher": "AES-256-GCM",
            "handshake_duration_ms": 150
        },
        "user_info": {
            "username": "admin",
            "role": "administrator",
            "permissions": ["read", "write", "admin"]
        }
    },
    "reference": "conn-12345",
    "additional_data": {
        "geo_location": {
            "country": "US",
            "region": "CA",
            "coordinates": {
                "lat": 37.7749,
                "lon": -122.4194
            }
        },
        "device_info": {
            "os": "Linux",
            "version": "Ubuntu 22.04",
            "kernel": "5.15.0"
        }
    }
}

def main():
    print("=" * 60)
    print("GELF Field Flattening Demonstration")
    print("=" * 60)
    
    # Create GELF message
    gelf_message = GELFMessage.from_netbird_event(
        event_data=sample_event,
        host="nb_streamer",
        tenant_id="n2con"
    )
    
    # Get the full message dictionary
    gelf_dict = gelf_message.dict()
    
    print("\nGenerated GELF Fields:")
    print("-" * 40)
    
    # Show standard GELF fields
    standard_fields = ['version', 'host', 'short_message', 'timestamp', 'level', 'facility']
    print("\n📋 Standard GELF Fields:")
    for field in standard_fields:
        if field in gelf_dict:
            value = gelf_dict[field]
            if field == 'timestamp':
                value = f"{value} (Unix timestamp)"
            print(f"   {field}: {value}")
    
    # Show all NB_ prefixed fields (our flattened Netbird fields)
    nb_fields = {k: v for k, v in gelf_dict.items() if k.startswith('_NB_')}
    
    print(f"\n🔍 Flattened Netbird Fields ({len(nb_fields)} total):")
    for field, value in sorted(nb_fields.items()):
        # Truncate long values for display
        display_value = str(value)
        if len(display_value) > 50:
            display_value = display_value[:47] + "..."
        print(f"   {field}: {display_value}")
    
    print(f"\n📊 Field Statistics:")
    print(f"   Total GELF fields: {len(gelf_dict)}")
    print(f"   Netbird fields: {len(nb_fields)}")
    print(f"   Standard fields: {len(gelf_dict) - len(nb_fields)}")
    
    print(f"\n🎯 Key Flattened Fields for Graylog Filtering:")
    key_fields = [
        '_NB_meta_source_addr',
        '_NB_meta_destination_addr', 
        '_NB_meta_port',
        '_NB_meta_protocol',
        '_NB_meta_connection_info_encrypted',
        '_NB_meta_user_info_username',
        '_NB_additional_data_geo_location_country',
        '_NB_additional_data_device_info_os'
    ]
    
    for field in key_fields:
        if field in nb_fields:
            print(f"   {field}: {nb_fields[field]}")
    
    print(f"\n💡 Graylog Search Examples:")
    print(f"   Find all n2con events: _NB_tenant:\"n2con\"")
    print(f"   Find TCP connections: _NB_meta_protocol:\"TCP\"")
    print(f"   Find encrypted connections: _NB_meta_connection_info_encrypted:\"True\"")
    print(f"   Find admin user actions: _NB_meta_user_info_username:\"admin\"")
    print(f"   Find US connections: _NB_additional_data_geo_location_country:\"US\"")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
