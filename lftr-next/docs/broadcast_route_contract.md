# Broadcast/Watch Route Contract

This is the required clean contract for future pass #9. The current checkpoint documents the contract only; it does not activate these routes.

## Final user surfaces

| Surface | Method | Path | Purpose |
| --- | --- | --- | --- |
| Broadcaster page | `GET` | `/broadcast` | One responsive broadcaster UI for mobile and desktop. |
| Watch page | `GET` | `/watch` | One responsive viewer UI for mobile and desktop. |
| Status | `GET` | `/api/broadcast/status` | Optional diagnostics/status without secrets. |

## Final WebSockets

| Socket | Path | Purpose |
| --- | --- | --- |
| Broadcast signaling | `/ws/broadcast` | Broadcaster presence, WebRTC offers/answers/ICE, media state. |
| Watch signaling | `/ws/watch` | Viewer presence, WebRTC offers/answers/ICE, playback state. |
| Chat | `/ws/chat` | Text chat, STT transcript events, AI bridge replies, attachments, web-search results. |

## Message families to preserve

- `presence`: broadcaster connected, viewer count, room state.
- `signaling`: offer, answer, ICE candidate, renegotiation diagnostics.
- `chat`: user text, broadcaster text, watcher text, system notices.
- `stt`: chunk accepted/rejected, final transcript, retry/backoff status.
- `ai`: reply text, optional voice payload hook, status/error events.
- `upload`: image attachment metadata and optional media-upload status.
- `debug`: browser permission, media device, WebRTC, and socket status.

## Forbidden route sprawl

Future implementation must not add:

- `/broadcast2`
- `/watch2`
- old GFS-prefixed broadcaster aliases
- mixed broadcast/globe route aliases
- duplicate chat socket paths
- duplicate media loops

## Minimal status response sketch

```json
{
  "ok": true,
  "enabled": true,
  "rooms": 1,
  "routes": ["/broadcast", "/watch"],
  "websockets": ["/ws/broadcast", "/ws/watch", "/ws/chat"],
  "degraded": false
}
```

The status endpoint must not reveal credentials, room secrets, upload paths outside public URLs, API keys, or database DSNs.
