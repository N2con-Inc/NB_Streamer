# NetBird Webhook Bug Workaround

## Issue Description

NetBird has a bug where the `meta` field in webhook payloads contains Go map syntax instead of proper JSON when using custom webhook body templates.

### Bug Details

**Trigger**: Occurs when modifying NetBird's webhook body template to include custom fields (e.g., adding `NB_Tenant`)

**Problem**: The `{{.Event.Meta}}` template variable outputs Go map string representation instead of JSON object:

```json
// Expected (proper JSON):
{
  "meta": {
    "destination_addr": "10.0.1.5:8266", 
    "received_timestamp": "2025-08-28T23:31:16.312Z"
  }
}

// Actual (Go map as string):
{
  "meta": "map[destination_addr:10.0.1.5:8266 received_timestamp:2025-08-28 23:31:16.312662603 &#43;0000 UTC]"
}
```

**Additional Issues**:
- HTML entities: `+` encoded as `&#43;`
- Go timestamp format instead of ISO 8601
- Requires custom parsing instead of standard JSON

## Current Workaround

**Version**: 0.5.1 implements a workaround for this NetBird bug:

1. **Go Map Parser**: Parses `map[key:value ...]` syntax from `meta` field
2. **HTML Entity Decoding**: Converts `&#43;` back to `+` 
3. **Timestamp Conversion**: Converts Go timestamps to ISO 8601 format
4. **Field Extraction**: Extracts structured data from Go map string

## Code Location

The workaround is implemented in:
- `src/models/gelf.py`: `parse_go_map()` and `convert_go_timestamp_to_iso()`
- `src/models/gelf.py`: `parse_json_fields()` automatically detects and parses Go maps

## Future Action Required

**When NetBird fixes this bug**:

1. **Remove Go Map Processing**: Delete `parse_go_map()` function and related code
2. **Simplify Field Processing**: Remove Go map detection from `parse_json_fields()`
3. **Update Tests**: Remove Go map parsing tests
4. **Standard JSON Only**: Rely on native JSON parsing for `meta` field

## Bug Report Status

Bug reported to NetBird GitHub repository. This workaround will be removed once NetBird properly serializes the `meta` field as JSON object.

**GitHub Issue**: [Link to be added when filed]

## Version History

- **0.5.0**: Initial timestamp fix
- **0.5.1**: Complete NetBird bug workaround (HTML entities + Go map parsing)
- **Future**: Remove workaround when NetBird is fixed
