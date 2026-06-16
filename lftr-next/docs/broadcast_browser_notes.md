# Broadcast/Watch Browser Notes

These notes capture browser behavior for future pass #9. They are not runtime code.

## Chrome

- Speech-to-text typically works well through browser speech APIs or capture-friendly audio paths.
- Mobile camera switching may require explicit `facingMode` handling and visible permission status.
- Autoplay and WebRTC playback often require muted video or a user gesture before unmuted playback.
- Screen-sharing and mobile behavior may differ by OS and Chrome version.

## Firefox

- The AI/chat path previously behaved well in Firefox-oriented testing.
- Speech-to-text availability and browser speech APIs may differ from Chrome.
- Media-device labels may remain hidden until permissions are granted.
- Autoplay behavior may require explicit user gestures and clear UI state.

## Shared implementation notes

- Mobile and desktop should use the same `/broadcast` and `/watch` pages.
- Camera front/back switching should be an explicit UI action, not a separate route.
- Permission state belongs in a status/debug panel, not hardcoded into route variants.
- WebRTC offer/answer/ICE failures should surface in debug/status events.
- Upload and web-search panes should be hooks that can be disabled cleanly.
- No GFS renderer should load by default on broadcast/watch pages.
