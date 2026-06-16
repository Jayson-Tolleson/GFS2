import type { BBox } from './field';

export interface ReportPoint { id: string; kind: 'report'; title: string; latitude: number; longitude: number; observed_at: string; summary: string; source: string; }
export interface SpatialFeature { id: string; kind: string; label: string; latitude?: number | null; longitude?: number | null; metadata: Record<string, unknown>; }
export interface ViewportSpatialResponse { ok: boolean; bbox: BBox; tier: string; reports: ReportPoint[]; lakes: SpatialFeature[]; harbors: SpatialFeature[]; coast_mask: Record<string, unknown>; postgis: Record<string, unknown>; }
