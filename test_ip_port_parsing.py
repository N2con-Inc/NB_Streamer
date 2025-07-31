#!/usr/bin/env python3
"""Test script to demonstrate the IP:port parsing functionality."""

import json
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.gelf import GELFMessage

# Sample Netbird event with IP:port combinations
sample_event = {
    "ID": "ip-port-demo-001",
    "Timestamp": "2025-07-31T22:52:00Z",
    "Message": "Connection established with port separation",
    "InitiatorID": "user@n2con.com",
    "target_id": "server-001",
    "event_type": "connection",
    "action": "connect",
    "meta": {
        "source_addr": "192.168.68.141:54615",
        "destination_addr": "10.0.1.244:80",
        "protocol": "TCP",
        "bytes_sent": 2048,
        "bytes_received": 4096,
        "connection_info": {
            "encrypted": True,
            "cipher": "TLS-1.3",
            "handshake_duration_ms": 120
        }
    },
    "network_data": {
        "remote_addr": "203.0.113.45:443",
        "local_addr": "192.168.1.100:8080",
        "peer_addr": "172.16.0.50:22"
    },
    "additional_info": {
        "client_addr": "10.10.10.10:9999",
        "server_endpoint": "api.example.com:8443"
    }
}

def main():
    print("=" * 70)
    print("IP:Port Parsing Demonstration")
    print("=" * 70)
    
    # Create GELF message
    gelf_message = GELFMessage.from_netbird_event(
        event_data=sample_event,
        host="nb_streamer",
        tenant_id="n2con"
    )
    
    # Get the full message dictionary
    gelf_dict = gelf_message.dict()
    
    # Show all NB_ prefixed fields
    nb_fields = {k: v for k, v in gelf_dict.items() if k.startswith('_NB_')}
    
    print("\n🔍 Original vs Parsed Fields:")
    print("-" * 50)
    
    # Group fields by their relationship
    address_groups = {}
    for field, value in sorted(nb_fields.items()):
        if any(addr_type in field for addr_type in ['_addr', '_address']):
            base_name = field.replace('_addr', '').replace('_address', '')
            if base_name not in address_groups:
                address_groups[base_name] = {}
            address_groups[base_name]['addr'] = value
        elif '_port' in field:
            base_name = field.replace('_port', '')
            if base_name not in address_groups:
                address_groups[base_name] = {}
            address_groups[base_name]['port'] = value
    
    print("\n📍 Address and Port Field Pairs:")
    for base_name, fields in sorted(address_groups.items()):
        if 'addr' in fields and 'port' in fields:
            addr_field = f"{base_name}_addr" if not base_name.endswith('_addr') else base_name
            port_field = f"{base_name}_port" if not base_name.endswith('_port') else base_name.replace('_addr', '_port')
            print(f"   {addr_field}: {fields['addr']}")
            print(f"   {port_field}: {fields['port']}")
            print()
    
    print("🎯 Key Network Fields for Graylog:")
    print("-" * 40)
    
    # Highlight key network fields
    key_network_fields = [
        '_NB_meta_source_addr', '_NB_meta_source_port',
        '_NB_meta_destination_addr', '_NB_meta_destination_port',
        '_NB_network_data_remote_addr', '_NB_network_data_remote_port',
        '_NB_network_data_local_addr', '_NB_network_data_local_port',
        '_NB_additional_info_client_addr', '_NB_additional_info_client_port'
    ]
    
    for field in key_network_fields:
        if field in nb_fields:
            field_type = "🌐 IP" if '_addr' in field else "🔌 Port"
            print(f"   {field_type} {field}: {nb_fields[field]}")
    
    print(f"\n💡 Enhanced Graylog Search Examples:")
    print(f"   # Find connections from specific IP")
    print(f"   _NB_meta_source_addr:\"192.168.68.141\"")
    print(f"   ")
    print(f"   # Find connections to specific port")
    print(f"   _NB_meta_destination_port:\"80\"")
    print(f"   ")
    print(f"   # Find SSH connections (port 22)")
    print(f"   _NB_network_data_peer_port:\"22\"")
    print(f"   ")
    print(f"   # Find HTTPS traffic")
    print(f"   _NB_network_data_remote_port:\"443\"")
    print(f"   ")
    print(f"   # Combine IP and port filters")
    print(f"   _NB_meta_source_addr:\"192.168.68.*\" AND _NB_meta_destination_port:\"80\"")
    print(f"   ")
    print(f"   # High port numbers (ephemeral ports)")
    print(f"   _NB_meta_source_port:>49152")
    
    print(f"\n📊 Network Analysis Benefits:")
    print(f"   ✅ Separate IP and port filtering")
    print(f"   ✅ Range queries on port numbers")
    print(f"   ✅ Subnet-based filtering on IPs")
    print(f"   ✅ Better dashboard visualizations")
    print(f"   ✅ Easier network security analysis")
    
    print(f"\n🔧 Field Statistics:")
    addr_fields = len([f for f in nb_fields.keys() if '_addr' in f])
    port_fields = len([f for f in nb_fields.keys() if '_port' in f])
    total_network = addr_fields + port_fields
    
    print(f"   Address fields: {addr_fields}")
    print(f"   Port fields: {port_fields}")
    print(f"   Total network fields: {total_network}")
    print(f"   Total GELF fields: {len(gelf_dict)}")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
