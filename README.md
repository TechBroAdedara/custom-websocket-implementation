# Custom-WebSocket-Implementation
Custom WebSocket implementation I designed myself on a whim, in 2 days.

## Inspiration
The initial idea to use a global WebSocket manager was inspired by Starlette's own docs about WebSockets. 
But I quickly saw the need to include a pipeline that supported multiple WebSocket managers. 
In this application, I implemented two WebSocket managers: ChatWebsocketManager and NotificationWebSocketManager.
I decided to split the WebSocket connections into two because I needed to optimize the server load and memory usage. 
If you are building an app that only needs chat functionality "on the side" but needs notifications delivered every time, I want to optimize memory by disconnecting the chat WebSocket when it's not needed, but still be connected to the notification WebSocket. I might be wrong with this concern, so I am hoping someone corrects and educates me on it if I am. 

## WebSocket Managers
- Base Websocket Manager - Defines the common methods for all websocket managers and defines abstract methods that need to be implemented on a per-manager basis.
- Chat WebSocket Manager - Defines chat-specific listen and publish methods.
- Notification WebSocket Manager - Defines notification-specific listen and publish methods.
