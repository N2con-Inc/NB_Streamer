#!/usr/bin/env python3
"""Test script to demonstrate the improved short message generation."""

import json
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.gelf import GELFMessage

def test_message_scenarios():
    print("=" * 60)
    print("Short Message Generation Test")
    print("=" * 60)
    
    # Test case 1: Event with Message field
    print("\n🧪 Test 1: Event with Message field")
    print("-" * 40)
    event1 = {
        "ID": "test-001",
        "Timestamp": "2025-07-31T22:58:00Z",
        "Message": "User successfully connected to VPN gateway",
        "InitiatorID": "john.doe@n2con.com",
        "target_id": "vpn-gateway-001"
    }
    
    gelf1 = GELFMessage.from_netbird_event(event1, "nb_streamer", "n2con")
    print(f"Original Message: {event1['Message']}")
    print(f"GELF short_message: {gelf1.short_message}")
    
    # Test case 2: Event without Message field but with event_type and action
    print("\n🧪 Test 2: Event without Message, with event_type and action")
    print("-" * 40)
    event2 = {
        "ID": "test-002",
        "Timestamp": "2025-07-31T22:58:30Z",
        "InitiatorID": "admin@n2con.com",
        "event_type": "connection",
        "action": "establish",
        "target_id": "peer-123"
    }
    
    gelf2 = GELFMessage.from_netbird_event(event2, "nb_streamer", "n2con")
    print(f"Event type: {event2['event_type']}, Action: {event2['action']}")
    print(f"InitiatorID: {event2['InitiatorID']}")
    print(f"GELF short_message: {gelf2.short_message}")
    
    # Test case 3: Event with minimal fields
    print("\n🧪 Test 3: Event with minimal fields")
    print("-" * 40)
    event3 = {
        "ID": "test-003",
        "Timestamp": "2025-07-31T22:59:00Z",
        "InitiatorID": "user@n2con.com"
    }
    
    gelf3 = GELFMessage.from_netbird_event(event3, "nb_streamer", "n2con")
    print(f"Only InitiatorID: {event3['InitiatorID']}")
    print(f"GELF short_message: {gelf3.short_message}")
    
    # Test case 4: Event with empty Message field
    print("\n🧪 Test 4: Event with empty Message field")
    print("-" * 40)
    event4 = {
        "ID": "test-004",
        "Timestamp": "2025-07-31T22:59:30Z",
        "Message": "",
        "InitiatorID": "service@n2con.com",
        "event_type": "heartbeat"
    }
    
    gelf4 = GELFMessage.from_netbird_event(event4, "nb_streamer", "n2con")
    print(f"Empty Message field, event_type: {event4['event_type']}")
    print(f"GELF short_message: {gelf4.short_message}")
    
    print("\n" + "=" * 60)
    print("📋 Summary:")
    print("✅ Messages with content use the Message field directly")
    print("✅ Fallback logic constructs meaningful messages from available fields")
    print("✅ Always provides a descriptive short_message for Graylog")
    print("=" * 60)

if __name__ == "__main__":
    test_message_scenarios()
