# NB_Streamer v0.5.1 - NetBird Webhook Bug Workaround

## 🐛 Bug Fix Release

This release fixes critical parsing issues when using NetBird with custom webhook body templates.

## 🔧 What's Fixed

### NetBird Webhook Parsing Issue
- **Problem**: NetBird sends `meta` field as Go map string instead of JSON object when using custom webhook templates
- **Impact**: Events failed to parse and index in Graylog with OpenSearch date parsing errors
- **Solution**: Automatic detection and parsing of Go map syntax with proper field extraction

### Specific Fixes
- ✅ **Go Map Parser**: Handles `map[key:value ...]` syntax from NetBird `meta` field
- ✅ **HTML Entity Decoding**: Converts `&#43;` back to `+` in timestamps
- ✅ **Timestamp Conversion**: Go format → ISO 8601 (`2025-08-28T23:31:16.312Z`)
- ✅ **GELF Compression**: Disabled to prevent JSON parsing errors in Graylog
- ✅ **OpenSearch Compatibility**: Proper date field formatting for indexing

## 📋 Root Cause Analysis

**Trigger**: This bug appears when customizing NetBird's webhook body template (e.g., adding `NB_Tenant` field)

**NetBird Bug**: The `{{.Event.Meta}}` template variable outputs:
```json
// Expected:
"meta": { "received_timestamp": "2025-08-28T23:31:16.312Z" }

// Actual:  
"meta": "map[received_timestamp:2025-08-28 23:31:16.312662603 &#43;0000 UTC]"
```

## 🚀 Technical Implementation

- **Automatic Detection**: Code automatically detects Go map syntax in `meta` field
- **Backwards Compatible**: Works with both proper JSON and Go map format
- **Clean Architecture**: Workaround code clearly marked for removal when NetBird fixes upstream bug

## 📚 Documentation

- Added `NETBIRD_BUG_WORKAROUND.md` with full technical details
- Updated `README.md` with known issues section
- Added comprehensive `CHANGELOG.md`
- Code comments mark workaround functions for future removal

## 🔄 Deployment

```bash
docker pull your-registry/nb-streamer:0.5.1
# or
docker build -t nb-streamer:0.5.1 .
```

## 🚨 Important Notes

- **Temporary Fix**: This workaround will be **removed** when NetBird fixes the upstream bug
- **Bug Reported**: Issue filed with NetBird project
- **Full Compatibility**: Works with both standard and custom NetBird webhook templates

## 🎯 Verification

After deploying v0.5.1, verify in Graylog:
- ✅ No more OpenSearch date parsing errors
- ✅ `NB_meta_received_timestamp` fields properly formatted as ISO 8601
- ✅ Events indexing successfully with all meta fields extracted

---

**Full Changelog**: [CHANGELOG.md](./CHANGELOG.md)
**Bug Details**: [NETBIRD_BUG_WORKAROUND.md](./NETBIRD_BUG_WORKAROUND.md)
