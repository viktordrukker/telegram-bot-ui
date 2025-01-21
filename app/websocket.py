import asyncio
import json
import jwt
from datetime import datetime
from flask import current_app
import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, Set[asyncio.Queue]] = {}
        self.user_connections: Dict[str, Set[asyncio.Queue]] = {}

    async def register(self, user_id: str, queue: asyncio.Queue):
        """Register a new WebSocket connection"""
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(queue)
        logger.info(f'Registered WebSocket connection for user {user_id}')

    async def unregister(self, user_id: str, queue: asyncio.Queue):
        """Unregister a WebSocket connection"""
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(queue)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        logger.info(f'Unregistered WebSocket connection for user {user_id}')

    async def subscribe_to_bot(self, bot_id: str, queue: asyncio.Queue):
        """Subscribe to bot events"""
        if bot_id not in self.connections:
            self.connections[bot_id] = set()
        self.connections[bot_id].add(queue)

    async def unsubscribe_from_bot(self, bot_id: str, queue: asyncio.Queue):
        """Unsubscribe from bot events"""
        if bot_id in self.connections:
            self.connections[bot_id].discard(queue)
            if not self.connections[bot_id]:
                del self.connections[bot_id]

    async def broadcast_to_bot(self, bot_id: str, message: dict):
        """Broadcast a message to all connections subscribed to a bot"""
        if bot_id in self.connections:
            message_json = json.dumps(message)
            for queue in self.connections[bot_id]:
                await queue.put(message_json)

    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to a specific user"""
        if user_id in self.user_connections:
            message_json = json.dumps(message)
            for queue in self.user_connections[user_id]:
                await queue.put(message_json)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients"""
        message_json = json.dumps(message)
        for connections in self.user_connections.values():
            for queue in connections:
                await queue.put(message_json)

ws_manager = WebSocketManager()

async def websocket_handler(websocket, path):
    """Handle WebSocket connections"""
    queue = asyncio.Queue()
    user_id = None
    
    try:
        # Authenticate the connection
        auth_token = websocket.request_headers.get('Authorization', '').replace('Bearer ', '')
        if not auth_token:
            await websocket.close(1008, 'Missing authentication token')
            return

        try:
            payload = jwt.decode(auth_token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['public_id']
        except jwt.InvalidTokenError:
            await websocket.close(1008, 'Invalid authentication token')
            return

        # Register the connection
        await ws_manager.register(user_id, queue)

        # Send initial connection message
        await websocket.send(json.dumps({
            'type': 'connection',
            'status': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }))

        # Start message handling tasks
        receive_task = asyncio.create_task(handle_incoming_messages(websocket, user_id))
        send_task = asyncio.create_task(handle_outgoing_messages(websocket, queue))

        # Wait for either task to complete
        done, pending = await asyncio.wait(
            [receive_task, send_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel pending tasks
        for task in pending:
            task.cancel()

    except Exception as e:
        logger.error(f'WebSocket error: {str(e)}')
    finally:
        # Clean up
        if user_id:
            await ws_manager.unregister(user_id, queue)

async def handle_incoming_messages(websocket, user_id):
    """Handle incoming WebSocket messages"""
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                message_type = data.get('type')

                if message_type == 'subscribe':
                    bot_id = data.get('bot_id')
                    if bot_id:
                        await ws_manager.subscribe_to_bot(bot_id, websocket)
                elif message_type == 'unsubscribe':
                    bot_id = data.get('bot_id')
                    if bot_id:
                        await ws_manager.unsubscribe_from_bot(bot_id, websocket)
                # Add more message type handlers as needed

            except json.JSONDecodeError:
                logger.error('Invalid JSON message received')
    except Exception as e:
        logger.error(f'Error handling incoming messages: {str(e)}')

async def handle_outgoing_messages(websocket, queue):
    """Handle outgoing WebSocket messages"""
    try:
        while True:
            message = await queue.get()
            await websocket.send(message)
    except Exception as e:
        logger.error(f'Error handling outgoing messages: {str(e)}')

def send_notification(user_id: str, notification_type: str, data: dict):
    """Send a notification to a user"""
    message = {
        'type': 'notification',
        'notification_type': notification_type,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }
    asyncio.create_task(ws_manager.send_to_user(user_id, message))

def broadcast_event(event_type: str, data: dict):
    """Broadcast an event to all connected clients"""
    message = {
        'type': 'event',
        'event_type': event_type,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }
    asyncio.create_task(ws_manager.broadcast(message))