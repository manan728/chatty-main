# Socket.IO Client Connection Guide

## Overview

Socket.IO is already implemented in the Chatty Backend! This guide shows you how to connect a client application to receive real-time updates when messages are posted.

## Socket.IO Server Configuration

**Server URL:** `http://localhost:8000/socket.io`  
**Server Status:** ✅ Already running and configured

## Available Events

### Client → Server (Events you emit)

1. **`connect`** - Automatically handled when client connects
2. **`join`** - Join a chatroom to receive messages
   ```json
   {
     "user_id": "uuid-here",
     "chatroom_id": "uuid-here"
   }
   ```
3. **`leave`** - Leave a chatroom
   ```json
   {
     "user_id": "uuid-here",
     "chatroom_id": "uuid-here"
   }
   ```
4. **`disconnect`** - Automatically handled when client disconnects

### Server → Client (Events you listen for)

1. **`joined`** - Confirmation that you joined a chatroom
   ```json
   {
     "chatroom_id": "uuid-here"
   }
   ```

2. **`left`** - Confirmation that you left a chatroom
   ```json
   {
     "chatroom_id": "uuid-here"
   }
   ```

3. **`new_message`** - Real-time message notification (emitted when someone posts via REST API)
   ```json
   {
     "id": "message-uuid",
     "message_text": "Hello world!",
     "user_id": "user-uuid",
     "chatroom_id": "chatroom-uuid",
     "is_reply": false,
     "parent_message_id": null,
     "created_date": "2024-01-01T12:00:00Z",
     "last_updated_date": "2024-01-01T12:00:00Z"
   }
   ```

4. **`error`** - Error messages from the server
   ```json
   {
     "message": "user_id and chatroom_id are required"
   }
   ```

## Client Examples

### Python Client

```python
import socketio
import asyncio

# Create Socket.IO client
sio = socketio.AsyncClient()

# Event handlers
@sio.event
async def connect():
    print("✅ Connected to server!")
    
    # Join a chatroom after connecting
    await sio.emit('join', {
        'user_id': 'your-user-uuid-here',
        'chatroom_id': 'your-chatroom-uuid-here'
    })

@sio.event
async def disconnect():
    print("❌ Disconnected from server")

@sio.event
async def joined(data):
    print(f"🎉 Joined chatroom: {data['chatroom_id']}")

@sio.event
async def left(data):
    print(f"👋 Left chatroom: {data['chatroom_id']}")

@sio.event
async def new_message(data):
    print(f"💬 New message in chatroom {data['chatroom_id']}:")
    print(f"   User: {data['user_id']}")
    print(f"   Message: {data['message_text']}")
    print(f"   Time: {data['created_date']}")

@sio.event
async def error(data):
    print(f"❌ Error: {data['message']}")

# Connect to server
async def main():
    await sio.connect('http://localhost:8000')
    await sio.wait()  # Keep connection alive

asyncio.run(main())
```

### JavaScript/TypeScript Client (Browser or Node.js)

```javascript
import { io } from 'socket.io-client';

// Connect to Socket.IO server
const socket = io('http://localhost:8000', {
  transports: ['websocket', 'polling']
});

// Event handlers
socket.on('connect', () => {
  console.log('✅ Connected to server!');
  
  // Join a chatroom after connecting
  socket.emit('join', {
    user_id: 'your-user-uuid-here',
    chatroom_id: 'your-chatroom-uuid-here'
  });
});

socket.on('disconnect', () => {
  console.log('❌ Disconnected from server');
});

socket.on('joined', (data) => {
  console.log(`🎉 Joined chatroom: ${data.chatroom_id}`);
});

socket.on('left', (data) => {
  console.log(`👋 Left chatroom: ${data.chatroom_id}`);
});

socket.on('new_message', (data) => {
  console.log(`💬 New message in chatroom ${data.chatroom_id}:`);
  console.log(`   User: ${data.user_id}`);
  console.log(`   Message: ${data.message_text}`);
  console.log(`   Time: ${data.created_date}`);
  
  // Update your UI with the new message
  addMessageToUI(data);
});

socket.on('error', (data) => {
  console.error(`❌ Error: ${data.message}`);
});

// Helper function to add message to UI
function addMessageToUI(message) {
  const messageList = document.getElementById('messages');
  const messageElement = document.createElement('div');
  messageElement.innerHTML = `
    <strong>${message.user_id}:</strong> ${message.message_text}
    <small>${new Date(message.created_date).toLocaleString()}</small>
  `;
  messageList.appendChild(messageElement);
}
```

### HTML Example (Browser)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Chatty Socket.IO Client</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
    <div id="messages"></div>
    <input type="text" id="messageInput" placeholder="Type a message...">
    <button onclick="sendMessage()">Send</button>

    <script>
        const socket = io('http://localhost:8000');
        const userId = 'your-user-uuid';  // Replace with actual user ID
        const chatroomId = 'your-chatroom-uuid';  // Replace with actual chatroom ID

        socket.on('connect', () => {
            console.log('Connected!');
            socket.emit('join', {
                user_id: userId,
                chatroom_id: chatroomId
            });
        });

        socket.on('new_message', (data) => {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.textContent = `${data.user_id}: ${data.message_text}`;
            messagesDiv.appendChild(messageDiv);
        });

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const messageText = input.value;
            
            // Send via REST API (Socket.IO will broadcast to room automatically)
            fetch('http://localhost:8000/messages/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message_text: messageText,
                    user_id: userId,
                    chatroom_id: chatroomId,
                    is_reply: false
                })
            }).then(() => {
                input.value = '';
            });
        }
    </script>
</body>
</html>
```

## Complete Workflow Example

1. **Create a user and chatroom** (via REST API):
```bash
# Create user
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "handle": "alice"}'

# Create chatroom
curl -X POST http://localhost:8000/chatrooms/ \
  -H "Content-Type: application/json" \
  -d '{"name": "general"}'

# Save the returned IDs (user_id and chatroom_id)
```

2. **Connect Socket.IO client** and join the chatroom

3. **Post messages** via REST API, and **receive them in real-time** via Socket.IO:
```bash
# Post message via REST API
curl -X POST http://localhost:8000/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "message_text": "Hello everyone!",
    "user_id": "user-uuid-from-step-1",
    "chatroom_id": "chatroom-uuid-from-step-1",
    "is_reply": false
  }'
```

4. **All connected clients** in that chatroom will receive the `new_message` event automatically!

## Testing

You can test Socket.IO using the existing smoke test:

```bash
cd app
poetry run pytest tests_smoke/smoke_socketio.py -v
```

## Requirements

### For Python Clients:
- Install: `pip install python-socketio[client]` or `pip install python-socketio` (async client)

### For JavaScript/TypeScript:
- Install: `npm install socket.io-client`
- Or use CDN: `<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>`

### CORS Configuration

The server allows connections from any origin by default (development mode). To restrict:
- Set `SOCKETIO_CORS_ORIGINS` environment variable
- Example: `SOCKETIO_CORS_ORIGINS=http://localhost:3000,https://yourdomain.com`

## Troubleshooting

1. **Connection refused?** Make sure the app is running on port 8000
2. **Not receiving messages?** Verify you've joined the correct chatroom with valid IDs
3. **CORS errors?** Check `SOCKETIO_CORS_ORIGINS` setting
4. **Events not firing?** Verify the event names match exactly (case-sensitive)

