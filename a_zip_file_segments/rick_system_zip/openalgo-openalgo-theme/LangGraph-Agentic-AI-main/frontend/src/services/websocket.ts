// frontend/src/services/websocket.js

export class SignalWebSocket {
  constructor(url = (process.env.REACT_APP_WS_URL || 'ws://websocket_server:8008/ws').trim()) {
    this.baseUrl = url;
    this.ws = null;
    this.reconnectInterval = 5000;
    this.maxReconnectAttempts = 5;
    this.reconnectAttempts = 0;
    this.clientId = this.generateClientId();
    this.isIntentionallyClosed = false;
    this.messageHandlers = new Map();
    this.connectionPromise = null;

    this.connect();
  }
  
  generateClientId = () => {
    return 'client_' + Math.random().toString(36).substr(2, 9);
  }
  
  connect = async () => {
    if (this.connectionPromise) {
      return this.connectionPromise;
    }
    
    this.connectionPromise = new Promise((resolve, reject) => {
      try {
        const wsUrl = `${this.baseUrl}/${this.clientId}`;
        console.log(`Attempting WebSocket connection to: ${wsUrl}`);
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = (event) => {
          console.log('✅ WebSocket connected successfully');
          this.reconnectAttempts = 0;
          this.isIntentionallyClosed = false;
          this.connectionPromise = null;
          
          this.send({
            type: 'ping',
            clientId: this.clientId
          });
          
          resolve(this.ws);
        };
        
        this.ws.onclose = (event) => {
          console.log(`WebSocket disconnected - Code: ${event.code}, Reason: ${event.reason}`);
          this.connectionPromise = null;
          
          if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
            const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts);
            console.log(`Scheduling reconnection in ${delay}ms (attempt ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
              this.reconnect();
            }, delay);
          } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ Max reconnection attempts reached');
            this.handleConnectionFailure();
          }
        };
        
        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.connectionPromise = null;
          reject(error);
        };
        
        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        setTimeout(() => {
          if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
            console.error('WebSocket connection timeout');
            this.ws.close();
            reject(new Error('Connection timeout'));
          }
        }, 10000);
        
      } catch (error) {
        console.error('Error creating WebSocket:', error);
        this.connectionPromise = null;
        reject(error);
      }
    });
    
    return this.connectionPromise;
  }
  
  reconnect = async () => {
    console.log(`🔄 Attempting to reconnect... (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
    this.reconnectAttempts++;
    
    if (this.ws) {
      this.ws.close();
    }
    
    try {
      await this.connect();
      console.log('✅ Reconnection successful');
    } catch (error) {
      console.error('❌ Reconnection failed:', error);
    }
  }
  
  handleMessage = (data) => {
    const handler = this.messageHandlers.get(data.type);
    if (handler) {
      handler(data);
    }
  }
  
  handleConnectionFailure = () => {
    const handler = this.messageHandlers.get('connection_failed');
    if (handler) {
      handler();
    }
  }
  
  onMessage = (messageType, callback) => {
    this.messageHandlers.set(messageType, callback);
  }
  
  onAgentStatus = (callback) => {
    return this.onMessage('agent_status', callback);
  }
  
  onAgentOutput = (callback) => {
    return this.onMessage('agent_output', callback);
  }
  
  onTaskUpdate = (callback) => {
    return this.onMessage('task_update', callback);
  }
  
  onSystemEvent = (callback) => {
    return this.onMessage('system_event', callback);
  }

  onMarketEvent = (callback) => {
    return this.onMessage('market_event', callback);
  }

  onAgentSignal = (callback) => {
    return this.onMessage('agent_signal', callback);
  }

  onTradeUpdate = (callback) => {
    return this.onMessage('trade_update', callback);
  }
  
  onConnectionFailed = (callback) => {
    return this.onMessage('connection_failed', callback);
  }
  
  send = async (data) => {
    try {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        console.log('WebSocket not ready, waiting for connection...');
        await this.connect();
      }
      
      if (this.ws.readyState === WebSocket.OPEN) {
        const message = {
          ...data,
          clientId: this.clientId,
          timestamp: new Date().toISOString()
        };
        this.ws.send(JSON.stringify(message));
        console.log('📤 Message sent:', message);
      } else {
        console.warn('⚠️ Cannot send message - WebSocket not open. Ready state:', this.ws.readyState);
        throw new Error('WebSocket connection not available');
      }
    } catch (error) {
      console.error('❌ Error sending message:', error);
      throw error;
    }
  }
  
  ping = async () => {
    return this.send({ type: 'ping' });
  }
  
  getStatus = async () => {
    return this.send({ type: 'get_status' });
  }
  
  createTask = async (taskData) => {
    return this.send({
      type: 'create_task',
      data: taskData
    });
  }
  
  close = () => {
    console.log('🔌 Closing WebSocket connection');
    this.isIntentionallyClosed = true;
    this.reconnectAttempts = this.maxReconnectAttempts;
    
    if (this.ws) {
      this.ws.close(1000, 'Client initiated close');
      this.ws = null;
    }
  }
  
  getConnectionStatus = () => {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting';
      case WebSocket.OPEN: return 'connected';
      case WebSocket.CLOSING: return 'closing';
      case WebSocket.CLOSED: return 'disconnected';
      default: return 'unknown';
    }
  }
  
  isConnected = () => {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}