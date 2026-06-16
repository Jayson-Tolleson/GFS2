export type BroadcastMessage = { family?: string; type: string; room?: string; text?: string; name?: string; payload?: unknown; [key: string]: unknown };

export class JsonSocket {
  private socket?: WebSocket;
  constructor(private readonly path: string, private readonly onMessage: (message: BroadcastMessage) => void, private readonly onStatus: (status: string) => void) {}
  connect(room = 'default') {
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    this.socket = new WebSocket(`${proto}://${window.location.host}${this.path}?room=${encodeURIComponent(room)}`);
    this.socket.onopen = () => this.onStatus(`${this.path} connected`);
    this.socket.onclose = () => this.onStatus(`${this.path} closed`);
    this.socket.onerror = () => this.onStatus(`${this.path} error`);
    this.socket.onmessage = (event) => { try { this.onMessage(JSON.parse(event.data)); } catch { this.onStatus('invalid JSON message'); } };
  }
  send(message: BroadcastMessage) { if (this.socket?.readyState === WebSocket.OPEN) this.socket.send(JSON.stringify(message)); }
  close() { this.socket?.close(); }
}
