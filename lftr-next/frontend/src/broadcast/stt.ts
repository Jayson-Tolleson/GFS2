type SpeechRecognitionCtor = new () => { continuous: boolean; interimResults: boolean; onresult: ((event: { results: ArrayLike<{ 0: { transcript: string }; isFinal: boolean }> }) => void) | null; onerror: (() => void) | null; start(): void; stop(): void };

declare global { interface Window { SpeechRecognition?: SpeechRecognitionCtor; webkitSpeechRecognition?: SpeechRecognitionCtor; } }

export class SttHook {
  private recognition?: InstanceType<SpeechRecognitionCtor>;
  constructor(private readonly onFinal: (text: string) => void, private readonly status: (line: string) => void) {}
  available() { return Boolean(window.SpeechRecognition || window.webkitSpeechRecognition); }
  start() {
    const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Ctor) { this.status('STT unsupported in this browser'); return; }
    this.recognition = new Ctor(); this.recognition.continuous = true; this.recognition.interimResults = true;
    this.recognition.onresult = (event) => { const latest = event.results[event.results.length - 1]; if (latest?.isFinal) this.onFinal(latest[0].transcript); };
    this.recognition.onerror = () => this.status('STT error'); this.recognition.start(); this.status('STT listening');
  }
  stop() { this.recognition?.stop(); this.status('STT stopped'); }
}
