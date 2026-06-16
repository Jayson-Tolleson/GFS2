import type { FieldStreamEvent } from '../types/stream';

export function openFieldStream(onEvent: (event: FieldStreamEvent) => void): EventSource {
  const source = new EventSource('/gfs/api/stream');
  for (const type of ['scene.heartbeat', 'atmosphere.field.patch', 'ocean.field.patch', 'reports.patch'] as const) {
    source.addEventListener(type, (event) => {
      const message = event as MessageEvent<string>;
      onEvent({ type, id: message.lastEventId, payload: JSON.parse(message.data), receivedAt: new Date().toISOString() });
    });
  }
  source.onerror = () => onEvent({ type: 'stream.error', payload: { message: 'SSE connection interrupted' }, receivedAt: new Date().toISOString() });
  return source;
}
