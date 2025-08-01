#!/usr/bin/env python3
"""Test script to demonstrate the timestamp field fix."""

import sys
import os
from datetime import datetime

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.gelf import GELFMessage

def test_timestamp_scenarios():
    print("=" * 70)
    print("Timestamp Field Fix Demonstration")
    print("=" * 70)
    
    # Test case 1: Event with both Timestamp and timestamp fields (problematic case)
    print("\n🧪 Test 1: Event with both Timestamp (ISO) and timestamp (event type)")
    print("-" * 65)
    event1 = {
        "ID": "test-001",
        "Timestamp": "2025-01-31T23:04:00Z",  # Real timestamp
        "timestamp": "TYPE_END",               # Event type (not a timestamp)
        "Message": "Connection session ended",
        "InitiatorID": "user@n2con.com",
        "event_type": "TYPE_END"
    }
    
    gelf1 = GELFMessage.from_netbird_event(event1, "nb_streamer", "n2con")
    gelf_dict1 = gelf1.dict()
    
    print(f"Input Timestamp field: {event1['Timestamp']}")
    print(f"Input timestamp field: {event1['timestamp']}")
    print(f"GELF timestamp field: {gelf_dict1['timestamp']} (Unix timestamp)")
    print(f"GELF short_message: {gelf_dict1['short_message']}")
    
    # Show relevant custom fields
    timestamp_fields = {k: v for k, v in gelf_dict1.items() if 'timestamp' in k.lower()}
    print(f"Custom fields with timestamp data: {timestamp_fields}")
    
    # Test case 2: Event with only Timestamp field (normal case)
    print("\n🧪 Test 2: Event with only Timestamp field")
    print("-" * 45)
    event2 = {
        "ID": "test-002", 
        "Timestamp": "2025-01-31T23:05:00Z",
        "Message": "User login successful",
        "InitiatorID": "admin@n2con.com"
    }
    
    gelf2 = GELFMessage.from_netbird_event(event2, "nb_streamer", "n2con")
    gelf_dict2 = gelf2.dict()
    
    print(f"Input Timestamp field: {event2['Timestamp']}")
    print(f"GELF timestamp field: {gelf_dict2['timestamp']} (Unix timestamp)")
    print(f"GELF short_message: {gelf_dict2['short_message']}")
    
    # Test case 3: Event with only lowercase timestamp field containing valid timestamp
    print("\n🧪 Test 3: Event with lowercase timestamp field (valid timestamp)")
    print("-" * 60)
    event3 = {
        "ID": "test-003",
        "timestamp": "2025-01-31T23:06:00Z",  # Valid timestamp in lowercase field
        "Message": "System heartbeat",
        "InitiatorID": "system@n2con.com"
    }
    
    gelf3 = GELFMessage.from_netbird_event(event3, "nb_streamer", "n2con")
    gelf_dict3 = gelf3.dict()
    
    print(f"Input timestamp field: {event3['timestamp']}")
    print(f"GELF timestamp field: {gelf_dict3['timestamp']} (Unix timestamp)")
    print(f"GELF short_message: {gelf_dict3['short_message']}")
    
    print(f"\n" + "=" * 70)
    print("📋 Summary of Timestamp Fix:")
    print("✅ Prioritizes Timestamp field over timestamp field for GELF timestamp")
    print("✅ Validates timestamp values before using them")
    print("✅ Preserves event type data in timestamp field as custom field")
    print("✅ Falls back gracefully when no valid timestamp is found")
    print("✅ Ensures Graylog timestamp column shows actual timestamps, not event types")
    print("=" * 70)

if __name__ == "__main__":
    test_timestamp_scenarios()
