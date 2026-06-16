export class BroadcastMedia {
  private stream?: MediaStream;
  private facingMode: 'user' | 'environment' = 'environment';
  constructor(private readonly video: HTMLVideoElement, private readonly status: (line: string) => void) {}
  async startCamera() {
    try {
      this.stopCamera();
      this.stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: this.facingMode }, audio: true });
      this.video.srcObject = this.stream;
      this.video.muted = true;
      await this.video.play().catch(() => undefined);
      this.status(`camera on (${this.facingMode})`);
    } catch (error) { this.status(`camera error: ${(error as Error).message}`); }
  }
  stopCamera() { this.stream?.getTracks().forEach((track) => track.stop()); this.stream = undefined; this.video.srcObject = null; this.status('camera stopped'); }
  switchCamera() { this.facingMode = this.facingMode === 'user' ? 'environment' : 'user'; return this.startCamera(); }
  async startMicrophoneOnly() {
    try { const audio = await navigator.mediaDevices.getUserMedia({ audio: true }); audio.getTracks().forEach((track) => track.stop()); this.status('microphone permission granted'); }
    catch (error) { this.status(`microphone error: ${(error as Error).message}`); }
  }
}
