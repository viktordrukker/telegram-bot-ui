class WebSocketService {
  constructor() {
    this.ws = null;
    this.subscribers = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectTimeout = 1000; // Start with 1 second
  }

  connect(token) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:51313/ws';
    this.ws = new WebSocket(`${wsUrl}?token=${token}`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.reconnectTimeout = 1000;
      this.notifySubscribers('connection', { status: 'connected' });
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.notifySubscribers(data.type, data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.notifySubscribers('connection', { status: 'disconnected' });
      this.attemptReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.notifySubscribers('error', { error });
    };
  }

  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached');
      return;
    }

    setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
      this.reconnectAttempts++;
      this.reconnectTimeout *= 2; // Exponential backoff
      this.connect();
    }, this.reconnectTimeout);
  }

  subscribe(type, callback) {
    if (!this.subscribers.has(type)) {
      this.subscribers.set(type, new Set());
    }
    this.subscribers.get(type).add(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.subscribers.get(type);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.subscribers.delete(type);
        }
      }
    };
  }

  notifySubscribers(type, data) {
    const callbacks = this.subscribers.get(type);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }
}

export const wsService = new WebSocketService();