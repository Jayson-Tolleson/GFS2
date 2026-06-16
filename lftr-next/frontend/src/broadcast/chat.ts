import { JsonSocket, type BroadcastMessage } from './signaling';

export class BroadcastChat {
  readonly socket: JsonSocket;
  constructor(private readonly log: HTMLElement, status: (line: string) => void) {
    this.socket = new JsonSocket('/ws/chat', (message) => this.add(message), status);
  }
  connect(room: string) { this.socket.connect(room); }
  send(text: string, name = 'Guest') { this.socket.send({ type: 'chat', text, name }); }
  sendTranscript(text: string) { this.socket.send({ type: 'stt', text, name: 'STT', final: true }); }
  requestAi() { this.socket.send({ type: 'ai' }); }
  sendUploadPlaceholder() { this.socket.send({ type: 'upload', metadata: { placeholder: true } }); }
  private add(message: BroadcastMessage) {
    const line = document.createElement('div');
    line.className = 'chat-line';
    line.textContent = `[${message.family ?? 'msg'}] ${message.name ? `${message.name}: ` : ''}${message.text ?? message.type}`;
    this.log.appendChild(line);
    this.log.scrollTop = this.log.scrollHeight;
  }
}
