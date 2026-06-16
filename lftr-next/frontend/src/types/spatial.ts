import type { BBox } from './field';

export interface ReportPoint { id: string; kind: 'report'; title: string; latitude: number; longitude: number; observed_at: string; summary: string; source: string; }
export interface SpatialFeature { id: string; stable_id?: string; kind: string; label?: string; name?: string; source?: string; area_km2?: number; label_point?: { lon: number; lat: number }; bbox?: number[]; geometry?: Record<string, unknown>; latitude?: number | null; longitude?: number | null; metadata?: Record<string, unknown>; properties?: Record<string, unknown>; }
export interface ViewportSpatialResponse { ok: boolean; bbox: BBox; tier: string; reports: ReportPoint[]; lakes: SpatialFeature[]; waterbodies: SpatialFeature[]; harbors: SpatialFeature[]; coast_mask: Record<string, unknown>; postgis: Record<string, unknown>; }
