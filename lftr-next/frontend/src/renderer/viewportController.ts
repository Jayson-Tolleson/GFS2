import type { BBox } from '../types/field';

type ViewportListener = (bbox: BBox) => void;

export class ViewportController {
  private timer: number | undefined;
  private listeners = new Set<ViewportListener>();

  constructor(private readonly debounceMs = 500) {}

  onChange(listener: ViewportListener): void { this.listeners.add(listener); }

  updateFromMockCamera(): void {
    const bbox = { west: -87.8, south: 18.0, east: -73.0, north: 32.5 };
    window.clearTimeout(this.timer);
    this.timer = window.setTimeout(() => this.emit(bbox), this.debounceMs);
  }

  private emit(bbox: BBox): void {
    for (const listener of this.listeners) listener(bbox);
  }
}
