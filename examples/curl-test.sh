#!/bin/bash
# Test script to send sample events to NB_Streamer

# Configuration
NB_STREAMER_URL="http://localhost:8000"
AUTH_TOKEN=""  # Set this if authentication is enabled

echo "🧪 Testing NB_Streamer..."

# Health check
echo "📋 Checking service health..."
curl -s "${NB_STREAMER_URL}/health" | jq '.' || echo "❌ Health check failed"

echo ""

# Send test event
echo "📤 Sending test event..."

if [ -n "$AUTH_TOKEN" ]; then
    # With authentication
    curl -X POST "${NB_STREAMER_URL}/events" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${AUTH_TOKEN}" \
        -d @test-event.json | jq '.' || echo "❌ Event sending failed"
else
    # Without authentication
    curl -X POST "${NB_STREAMER_URL}/events" \
        -H "Content-Type: application/json" \
        -d @test-event.json | jq '.' || echo "❌ Event sending failed"
fi

echo ""
echo "✅ Test complete! Check your Graylog for the processed event."
echo "Look for messages with _NB_tenant field matching your configuration."