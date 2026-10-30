# Custom WebSocket Managers

A FastAPI and Starlette WebSocket architecture with separate managers for chat and notification connections.

Rather than using one global WebSocket registry, each channel owns its connections and lifecycle. A shared pipeline authenticates the handshake, accepts the socket, starts the manager's listen loop, and cleans up on disconnect. This makes it possible to close chat connections independently of notification connections.

## Features

- JWT authentication during the WebSocket handshake.
- Shared `BaseWebsocketManager` for connection lifecycle and message helpers.
- Separate chat and notification managers with independent connection stores.
- Multiple active sockets per user.
- Pydantic validation for incoming and outgoing messages.
- Chat messages persisted through SQLAlchemy repositories.
- Chat messages published to the other participants in the room.
- Notification broadcast helper for system-wide messages.
- Graceful handling of invalid tokens, malformed messages, and disconnects.
- HTTP endpoints for creating rooms, listing rooms, and reading room history.
- Uvicorn and uv development workflow.

## Architecture

```mermaid
flowchart LR
    Client[Chat client] -->|WebSocket /chat/| ChatRouter[Chat router]
    Client -->|WebSocket /notification/| NotifRouter[Notification router]
    ChatRouter --> Pipeline[Auth and lifecycle pipeline]
    NotifRouter --> Pipeline
    Pipeline --> ChatManager[Chat manager]
    Pipeline --> NotifManager[Notification manager]
    ChatManager --> ChatService[Chat service]
    ChatService --> Repos[Repositories]
    Repos --> DB[(SQLAlchemy database)]
    ChatManager --> Store[(In-memory socket registry)]
    NotifManager --> Store
```

The registry is an in-memory `defaultdict` keyed by user ID. It is intentionally simple for the current single-process design.

## Tech stack

| Area | Technology |
| --- | --- |
| Language | Python 3.13 |
| Framework | FastAPI and Starlette |
| WebSockets | Starlette WebSocket support |
| Database | Async SQLAlchemy 2.x |
| Validation | Pydantic 2 |
| Auth | PyJWT access tokens |
| Packaging | uv |
| Server | Uvicorn |

## Project structure

```text
src/
  infra/
    websocket_pipeline.py          Handshake auth and manager lifecycle
    websockets/
      base_websocket_manager.py    Shared connection and message behavior
      chat_websocket_manager.py    Chat listen, persist, and publish logic
      notification_websocket_manager.py
  router/
    chat_router.py                 Chat WebSocket and room HTTP endpoints
    notification_router.py         Notification WebSocket and test endpoint
  services/
    chat_service.py                Chat room and message rules
  repositories/
    chat_repository.py             Database queries for rooms and messages
  models/
    chat.py                        ChatRoom, ChatMessage, ChatRoomUser
  schema/
    websocket_schema.py            Message request and response models
  settings.py                      Environment-backed configuration
```

## Getting started

### Prerequisites

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- A database supported by async SQLAlchemy

### Setup

```bash
git clone https://github.com/TechBroAdedara/custom-websocket-implementation.git
cd custom-websocket-implementation
uv sync
```

Create a `.env` file. The settings module requires the following values at startup:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/websocket_demo
ECHO_SQL=false

REDIS_CONNECTION_STRING=redis://localhost:6379/0
API_KEYS=["local-dev-key"]
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256

CLIENT_ID=your-oauth-client-id
CLIENT_SECRET=your-oauth-client-secret
REDIRECT_URI=http://localhost:8000/auth/callback
ENVIRONMENT=development

MAIL_USERNAME=your-smtp-username
MAIL_PASSWORD=your-smtp-password
MAIL_FROM=no-reply@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.example.com
MAIL_STARTTLS=true
MAIL_SSL_TLS=false
USE_CREDENTIALS=true
VALIDATE_CERTS=true
```

`API_KEYS` and `ADMIN_EMAILS` are list values and must be JSON arrays. `ADMIN_EMAILS` is optional and has a default in `src/settings.py`.

Start the API:

```bash
uv run uvicorn src.main:app --reload
```

- HTTP API: `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs`
- Chat WebSocket: `ws://127.0.0.1:8000/chat/`
- Notification WebSocket: `ws://127.0.0.1:8000/notification/`

### Database schema

The repository does not include migration tooling. Create the tables defined in `src/models` before using chat persistence.

### Authentication

The WebSocket pipeline reads a bearer token from the `Authorization` header:

```text
Authorization: Bearer <access_token>
```

Use a WebSocket client that supports custom headers. The browser `WebSocket` API cannot set an `Authorization` header directly.

This repository assumes users and access tokens are issued by an external auth service. It does not expose registration or login endpoints.

## API overview

| Area | Endpoint | Description |
| --- | --- | --- |
| Chat socket | `WS /chat/` | Authenticated chat connection |
| Notification socket | `WS /notification/` | Authenticated notification connection |
| Chat rooms | `POST /chat/rooms` | Create an empty chat room |
| Chat rooms | `GET /chat/rooms` | List the current user's rooms |
| Chat rooms | `GET /chat/rooms/{room_id}` | Read room history |
| Notifications | `POST /notification/user_id?user_id={user_id}` | Send a test notification |

### Chat message format

Send a JSON message over the chat socket:

```json
{
  "sender_id": "user-id",
  "chat_room_id": "room-id",
  "content": "Hello",
  "type": "chat"
}
```

The server stores the message and publishes it to the other room participants. The `sender_id` must match the authenticated user ID on the socket.

## Project status

This is a focused architecture demo rather than a production-ready chat product.

- The connection registry is process-local. Running multiple workers means sockets on different workers will not see each other's messages.
- Redis pub/sub is listed as the next step in the code but is not implemented yet.
- The notification manager can hold connections and broadcast test notifications, but its message-persistence method is still a stub.
- Chat room creation currently produces an empty room; participant management is not exposed by the HTTP API.
- Malformed messages close the chat socket with policy or payload errors.

## Contact

- Portfolio: [adedara-adeloro.cv](https://adedara-adeloro.cv)
- LinkedIn: [adedara-adeloro](https://www.linkedin.com/in/adedara-adeloro-813b9424b/)
- Email: [courageadedara@gmail.com](mailto:courageadedara@gmail.com)
