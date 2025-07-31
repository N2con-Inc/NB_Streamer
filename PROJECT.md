### Updated Software Development Plan: Netbird Event Streaming Receiver with GELF Output to Graylog

#### 1. Project Overview
**Objective**: Develop a lightweight HTTP service that acts as a generic endpoint for receiving streamed activity events from Netbird (as per the documentation at https://docs.netbird.io/how-to/stream-activity-to-generic-http). The service will parse incoming JSON events, transform them into GELF (Graylog Extended Log Format) messages, and forward them to an external Graylog instance. The entire setup will be containerized using Docker and designed to run behind an external reverse proxy (e.g., Nginx or Traefik) that handles TLS termination. This ensures the service itself listens on plain HTTP internally.

**Key Features**:
- Expose a single HTTP POST endpoint (e.g., `/events`) to receive Netbird events.
- Support optional authentication methods (None, Bearer Token, Basic Auth, Custom Header) to match Netbird's configuration options.
- Transform Netbird JSON events into GELF-compliant JSON, with custom Netbird fields prefixed as `NB_$FIELDNAME` (e.g., `NB_ID`, `NB_TIMESTAMP`, `NB_MESSAGE`, `NB_INITIATOR_ID`, `NB_TARGET_ID`, `NB_META` as a nested object, `NB_REFERENCE`).
- Send GELF messages via UDP (default) to the Graylog instance, with fallback support for TCP if needed.
- Configurable via environment variables for flexibility (e.g., Graylog host/port, auth secrets).
- Handle errors gracefully, logging failures without crashing the service.
- Minimal resource footprint for efficient Docker deployment.
- Include a user-friendly setup script that interactively prompts for configuration settings and generates a customized `docker-compose.yml` file.

**Assumptions**:
- Netbird will be configured to POST events to this endpoint with JSON payloads containing fields like `ID`, `Timestamp`, `Message`, `InitiatorID`, `TargetID`, `Meta`, and `Reference`.
- The external reverse proxy manages TLS, so the service uses HTTP internally (port 8080 by default).
- Graylog is externally hosted and accepts GELF input (typically UDP on port 12201).
- No custom body templates are used in Netbird; default JSON events are assumed.
- The service does not persist events; it's a stateless forwarder.
- Custom GELF fields will not include an leading underscore in the prefix to match the specified `NB_$FIELDNAME` format, but note that GELF best practices recommend underscores for additional fields to avoid key conflicts— this can be adjusted if issues arise.

**Scope Exclusions**:
- Implementing the reverse proxy or Graylog setup.
- Advanced features like event batching, retries beyond basic, or custom Netbird templates.
- Monitoring beyond basic logging.

#### 2. Requirements
**Functional Requirements**:
- Receive POST requests with JSON body matching Netbird's default event format.
- Validate authentication if enabled (e.g., check Bearer token against an env var).
- Map Netbird fields to GELF:
  - `version`: "1.1" (fixed).
  - `host`: Use `InitiatorID` or a configurable default (e.g., "netbird-streamer").
  - `short_message`: Netbird's `Message`.
  - `timestamp`: Netbird's `Timestamp` (converted to Unix timestamp if needed).
  - `level`: Default to 6 (INFO), or map based on event type if identifiable.
  - `full_message`: Concatenated details (e.g., `Message` + JSON-stringified `Meta`).
  - Custom fields: Prefix with `NB_` and use uppercase field names to match Netbird JSON keys (e.g., `NB_ID`, `NB_TIMESTAMP`, `NB_INITIATOR_ID`, `NB_TARGET_ID`, `NB_REFERENCE`, `NB_META` as a nested object).
- Send GELF JSON as a compressed UDP datagram to Graylog (use zlib compression as per GELF spec).
- Log incoming events and forwarding outcomes for debugging.
- Setup script: Interactively prompt for key env vars, validate inputs, and generate `docker-compose.yml`.

**Non-Functional Requirements**:
- Performance: Handle up to 100 events/second with low latency (<100ms per event).
- Security: Support auth to prevent unauthorized posts; run as non-root in Docker.
- Reliability: Graceful error handling (e.g., invalid JSON → 400 response; Graylog send failure → log and continue).
- Scalability: Stateless design allows horizontal scaling if needed.
- Configurability: All sensitive/external params via env vars (no hardcoding).
- Testing: Unit tests for mapping logic; integration tests with mock Netbird posts and Graylog receiver.
- Usability: Setup script should be intuitive, with defaults and validation (e.g., check if ports are numeric).

**Dependencies**:
- No external databases; pure in-memory processing.

#### 3. Architecture
**High-Level Design**:
- **Client (Netbird)** → **Reverse Proxy (TLS)** → **Docker Container (HTTP Service)** → **Graylog (GELF UDP)**.
- The service is a single-process HTTP server.
- Flow:
  1. Netbird POSTs JSON to `/events`.
  2. Service authenticates request (if enabled).
  3. Parses JSON, validates structure.
  4. Transforms to GELF JSON with `NB_` prefixed fields.
  5. Compresses and sends via UDP socket to Graylog.
  6. Responds with 200 OK (or error code) to Netbird.
- Setup script runs outside the container to generate deployment files.

**Text-Based Diagram**:
```
Netbird (Event Stream) --> HTTPS POST /events --> Reverse Proxy (TLS Termination)
                                                        |
                                                        v
Docker Container:
  - HTTP Server (e.g., FastAPI on port 8080)
    - Auth Middleware
    - Event Parser
    - GELF Transformer (with NB_ prefixes)
    - UDP Sender --> Graylog (UDP:12201)
```

**Data Flow Example**:
Incoming Netbird JSON:
```json
{
  "ID": "event-123",
  "Timestamp": "2025-07-30T12:00:00Z",
  "Message": "Peer connected",
  "InitiatorID": "peer-abc",
  "TargetID": "peer-def",
  "Meta": {"ip": "10.0.0.1"},
  "Reference": "https://netbird.io/log/123"
}
```
Transformed GELF:
```json
{
  "version": "1.1",
  "host": "peer-abc",
  "short_message": "Peer connected",
  "timestamp": 1756617600,
  "level": 6,
  "full_message": "Peer connected - Meta: {\"ip\": \"10.0.0.1\"}",
  "NB_ID": "event-123",
  "NB_TIMESTAMP": "2025-07-30T12:00:00Z",
  "NB_INITIATOR_ID": "peer-abc",
  "NB_TARGET_ID": "peer-def",
  "NB_REFERENCE": "https://netbird.io/log/123",
  "NB_META": {"ip": "10.0.0.1"}
}
```

#### 4. Technology Stack
- **Language**: Python 3.10+ (simple, readable; good for quick HTTP and socket ops).
- **HTTP Framework**: FastAPI (async-capable, auto-docs, easy validation).
- **GELF Handling**: Built-in (use `socket` for UDP, `json` for serialization, `zlib` for compression). Optionally use `graypy` library if bundled.
- **Logging**: Python's `logging` module, configurable to stdout for Docker.
- **Setup Script**: Python script using `input()` for prompts, `yaml` or template strings to generate `docker-compose.yml`.
- **Containerization**: Docker (base image: python:3.10-slim).
- **Testing**: Pytest for unit/integration; httpx for mock HTTP; socket mocks for UDP.
- **Other Tools**: Poetry or pip for dependency management; Git for version control.

#### 5. Implementation Steps
**Phase 1: Setup and Prototyping (1-2 days)**  
- Create a Git repo with basic structure: `app/main.py` (server), `app/gelf.py` (transformer), `tests/`, `setup.py` (setup script).
- Implement basic FastAPI app with `/events` POST endpoint.
- Add request parsing with Pydantic models based on Netbird event schema.
- Prototype GELF transformation function with `NB_` prefixes (e.g., map "ID" to "NB_ID").

**Phase 2: Core Features (2-3 days)**  
- Add authentication middleware:
  - Configurable via env vars (e.g., `AUTH_TYPE=none|bearer|basic|custom`, `AUTH_SECRET`).
  - For bearer: Check `Authorization: Bearer <token>` matches `AUTH_SECRET`.
  - Similar for basic (base64 decode) and custom header.
- Implement UDP sender: Compress GELF JSON and send to `GRAYLOG_HOST:GRAYLOG_PORT`.
- Add error handling: Try-except for parsing/sending; return appropriate HTTP codes (e.g., 401 Unauthorized, 500 Internal Error).
- Configure logging to output to console in JSON format for easy ingestion.

**Phase 3: Setup Script Development (1-2 days)**  
- Create `setup.py` (or `setup.sh` if preferring bash, but Python for cross-platform).
- Interactive prompts for:
  - AUTH_TYPE (default: none; validate against allowed options).
  - AUTH_SECRET (if auth enabled; mask input if possible).
  - AUTH_CUSTOM_HEADER (if custom auth).
  - GRAYLOG_HOST (required; no default).
  - GRAYLOG_PORT (default: 12201; validate numeric).
  - GRAYLOG_PROTOCOL (default: udp; validate udp/tcp).
  - DEFAULT_HOST (default: netbird-streamer).
  - PORT (default: 8080; validate numeric).
- Use templates to generate `docker-compose.yml`:
  - Include service definition with image, ports, environment vars populated from inputs.
  - Example snippet:
    ```yaml
    version: '3'
    services:
      netbird-receiver:
        image: your-repo/netbird-receiver:latest
        ports:
          - "${PORT}:8080"
        environment:
          AUTH_TYPE: "${AUTH_TYPE}"
          # ... other vars
    ```
- Validate generated file (e.g., check YAML syntax).
- Output instructions: "Run `docker-compose up -d` to start."

**Phase 4: Dockerization (1 day)**  
- Write `Dockerfile`:
  ```
  FROM python:3.10-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  USER nobody
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
  ```
- Use multi-stage build if needed for optimization.
- The setup script will generate `docker-compose.yml` for local/prod use.

**Phase 5: Configuration (0.5 day)**  
- Env vars (prompted in setup script):
  - `PORT`: Internal listen port (default: 8080).
  - `AUTH_TYPE`: Authentication method (default: none).
  - `AUTH_SECRET`: Token/password for auth.
  - `AUTH_CUSTOM_HEADER`: Name for custom auth (e.g., X-API-Key).
  - `GRAYLOG_HOST`: Graylog server IP/hostname.
  - `GRAYLOG_PORT`: Port (default: 12201).
  - `GRAYLOG_PROTOCOL`: udp|tcp (default: udp).
  - `DEFAULT_HOST`: Fallback GELF host field (default: netbird-streamer).

**Phase 6: Testing (1-2 days)**  
- **Unit Tests**: Test event-to-GELF mapping (verify `NB_` prefixes), auth validation.
- **Integration Tests**: Use curl/Postman to simulate Netbird POSTs; mock UDP socket to verify sends.
- **Setup Script Tests**: Mock inputs to verify generated `docker-compose.yml`; check for valid YAML and populated vars.
- **End-to-End**: Run setup script, deploy with generated compose, configure Netbird test event, check Graylog for receipt.
- Load test with tools like locust for 100+ events/sec.

**Phase 7: Documentation and Polish (1 day)**  
- README.md: Setup instructions (run `python setup.py` first), env vars, example configs, troubleshooting.
- API docs via FastAPI's Swagger UI.
- Add healthcheck endpoint (`/health`) for Docker.

#### 6. Timeline and Resources
- **Total Estimated Time**: 7-11 days for a single developer (added time for setup script).
- **Resources Needed**: Developer with Python/Docker experience; access to Netbird dashboard and Graylog for testing.
- **Risks and Mitigations**:
  - Netbird event format changes: Monitor docs; make parser flexible.
  - UDP packet loss: Add optional retries or use TCP.
  - Auth mismatches: Thorough testing with Netbird configs.
  - Setup script usability: Test with non-technical users; add help texts in prompts.
  - GELF field conflicts without underscore: If issues in Graylog, add option to prepend `_` to `NB_`.

#### 7. Deployment Notes
- Build and push Docker image to a registry (e.g., Docker Hub).
- Run the setup script to generate `docker-compose.yml`, then deploy.
- Deploy to a container orchestrator (e.g., Kubernetes, Docker Swarm) or simple server.
- Configure reverse proxy to forward `/events` to container's port 8080.
- Monitor container logs via Docker; scale if event volume increases.
- For production: Use secrets management (e.g., Docker secrets) for auth env vars; version the setup script outputs.
