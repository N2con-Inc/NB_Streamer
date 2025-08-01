#!/bin/bash

# NB_Streamer Monitoring Script
# Shows event processing statistics in a user-friendly format

STATS_URL="http://localhost:8001/stats"
HEALTH_URL="http://localhost:8001/health"

echo "=================================="
echo "      NB_Streamer Monitor         "
echo "=================================="
echo

# Check if service is running
if ! curl -s "$HEALTH_URL" >/dev/null 2>&1; then
    echo "❌ ERROR: NB_Streamer service is not responding"
    echo "   Check if the service is running on http://localhost:8001"
    exit 1
fi

echo "✅ Service is healthy"
echo

# Fetch and display statistics
STATS=$(curl -s "$STATS_URL")

if [ $? -ne 0 ] || [ -z "$STATS" ]; then
    echo "❌ ERROR: Could not fetch statistics"
    exit 1
fi

# Parse statistics using jq
TOTAL_RECEIVED=$(echo "$STATS" | jq -r '.statistics.total_events_received')
TOTAL_FORWARDED=$(echo "$STATS" | jq -r '.statistics.total_events_forwarded')
TOTAL_FAILED=$(echo "$STATS" | jq -r '.statistics.total_events_failed')
SUCCESS_RATE=$(echo "$STATS" | jq -r '.statistics.success_rate')
UPTIME=$(echo "$STATS" | jq -r '.statistics.uptime_seconds')
LAST_EVENT=$(echo "$STATS" | jq -r '.statistics.last_event_time // "Never"')

# Format uptime
UPTIME_FORMATTED=""
if [ "$UPTIME" != "null" ]; then
    HOURS=$((${UPTIME%.*} / 3600))
    MINUTES=$(((${UPTIME%.*} % 3600) / 60))
    SECONDS=$((${UPTIME%.*} % 60))
    
    if [ $HOURS -gt 0 ]; then
        UPTIME_FORMATTED="${HOURS}h ${MINUTES}m ${SECONDS}s"
    elif [ $MINUTES -gt 0 ]; then
        UPTIME_FORMATTED="${MINUTES}m ${SECONDS}s"
    else
        UPTIME_FORMATTED="${SECONDS}s"
    fi
fi

# Display main statistics
echo "📊 Event Processing Statistics:"
echo "   Total Received:  $TOTAL_RECEIVED"
echo "   Total Forwarded: $TOTAL_FORWARDED"
echo "   Total Failed:    $TOTAL_FAILED"
echo

# Success rate with emoji
if [ "$SUCCESS_RATE" = "1" ] || [ "$SUCCESS_RATE" = "1.0" ]; then
    echo "✅ Success Rate:    100%"
elif [ "$SUCCESS_RATE" = "0" ] || [ "$SUCCESS_RATE" = "0.0" ]; then
    echo "❌ Success Rate:    0%"
else
    PERCENT=$(echo "$SUCCESS_RATE * 100" | bc -l)
    echo "⚠️  Success Rate:    ${PERCENT%.*}%"
fi

echo "⏱️  Uptime:          $UPTIME_FORMATTED"

if [ "$LAST_EVENT" != "Never" ]; then
    echo "🕐 Last Event:      $LAST_EVENT"
else
    echo "🕐 Last Event:      Never"
fi

echo

# Show tenant breakdown
echo "👥 Events by Tenant:"
echo "$STATS" | jq -r '.statistics.events_by_tenant | to_entries[] | "   \(.key): \(.value.received) received, \(.value.forwarded) forwarded, \(.value.failed) failed"'

echo

# Show level breakdown
echo "📈 Events by Level:"
echo "$STATS" | jq -r '.statistics.events_by_level | to_entries[] | "   Level \(.key): \(.value) events"'

echo
echo "=================================="

# Optional: Watch mode
if [ "$1" = "--watch" ] || [ "$1" = "-w" ]; then
    echo "👁️  Watching for changes (press Ctrl+C to exit)..."
    echo
    while true; do
        sleep 5
        clear
        $0  # Re-run this script
    done
fi
