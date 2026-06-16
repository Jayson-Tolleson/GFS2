CREATE EXTENSION IF NOT EXISTS postgis;
CREATE SCHEMA IF NOT EXISTS {{SCHEMA}};

CREATE TABLE IF NOT EXISTS {{SCHEMA}}.spatial_metadata (
    key text PRIMARY KEY,
    value jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS {{SCHEMA}}.spatial_reports (
    id bigserial PRIMARY KEY,
    stable_id text NOT NULL UNIQUE,
    title text NOT NULL,
    source text NOT NULL DEFAULT 'csv',
    source_id text,
    kind text NOT NULL DEFAULT 'report',
    properties jsonb NOT NULL DEFAULT '{}'::jsonb,
    geom geometry(Point, 4326) NOT NULL,
    label_point geometry(Point, 4326),
    bbox geometry(Polygon, 4326),
    generated_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS spatial_reports_geom_gix ON {{SCHEMA}}.spatial_reports USING gist (geom);
CREATE INDEX IF NOT EXISTS spatial_reports_label_gix ON {{SCHEMA}}.spatial_reports USING gist (label_point);
CREATE INDEX IF NOT EXISTS spatial_reports_kind_idx ON {{SCHEMA}}.spatial_reports (kind);
CREATE INDEX IF NOT EXISTS spatial_reports_source_idx ON {{SCHEMA}}.spatial_reports (source, source_id);

CREATE TABLE IF NOT EXISTS {{SCHEMA}}.waterbodies (
    id bigserial PRIMARY KEY,
    stable_id text NOT NULL UNIQUE,
    name text NOT NULL,
    source text NOT NULL,
    source_id text,
    kind text NOT NULL DEFAULT 'waterbody',
    properties jsonb NOT NULL DEFAULT '{}'::jsonb,
    geom geometry(MultiPolygon, 4326) NOT NULL,
    label_point geometry(Point, 4326),
    bbox geometry(Polygon, 4326),
    generated_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS waterbodies_geom_gix ON {{SCHEMA}}.waterbodies USING gist (geom);
CREATE INDEX IF NOT EXISTS waterbodies_label_gix ON {{SCHEMA}}.waterbodies USING gist (label_point);
CREATE INDEX IF NOT EXISTS waterbodies_kind_idx ON {{SCHEMA}}.waterbodies (kind);
CREATE INDEX IF NOT EXISTS waterbodies_source_idx ON {{SCHEMA}}.waterbodies (source, source_id);

CREATE TABLE IF NOT EXISTS {{SCHEMA}}.harbors (
    id bigserial PRIMARY KEY,
    stable_id text NOT NULL UNIQUE,
    name text NOT NULL,
    source text NOT NULL,
    source_id text,
    kind text NOT NULL DEFAULT 'harbor',
    properties jsonb NOT NULL DEFAULT '{}'::jsonb,
    geom geometry(Point, 4326) NOT NULL,
    label_point geometry(Point, 4326),
    bbox geometry(Polygon, 4326),
    generated_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS harbors_geom_gix ON {{SCHEMA}}.harbors USING gist (geom);
CREATE INDEX IF NOT EXISTS harbors_label_gix ON {{SCHEMA}}.harbors USING gist (label_point);
CREATE INDEX IF NOT EXISTS harbors_kind_idx ON {{SCHEMA}}.harbors (kind);
CREATE INDEX IF NOT EXISTS harbors_source_idx ON {{SCHEMA}}.harbors (source, source_id);

CREATE TABLE IF NOT EXISTS {{SCHEMA}}.coast_masks (
    id bigserial PRIMARY KEY,
    stable_id text NOT NULL UNIQUE,
    name text NOT NULL,
    source text NOT NULL,
    source_id text,
    kind text NOT NULL DEFAULT 'coast_mask',
    tier text NOT NULL DEFAULT 'regional',
    properties jsonb NOT NULL DEFAULT '{}'::jsonb,
    geom geometry(MultiPolygon, 4326) NOT NULL,
    label_point geometry(Point, 4326),
    bbox geometry(Polygon, 4326),
    generated_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS coast_masks_geom_gix ON {{SCHEMA}}.coast_masks USING gist (geom);
CREATE INDEX IF NOT EXISTS coast_masks_label_gix ON {{SCHEMA}}.coast_masks USING gist (label_point);
CREATE INDEX IF NOT EXISTS coast_masks_kind_idx ON {{SCHEMA}}.coast_masks (kind);
CREATE INDEX IF NOT EXISTS coast_masks_source_idx ON {{SCHEMA}}.coast_masks (source, source_id);

CREATE TABLE IF NOT EXISTS {{SCHEMA}}.spatial_tiles (
    id bigserial PRIMARY KEY,
    stable_id text NOT NULL UNIQUE,
    name text NOT NULL,
    source text NOT NULL DEFAULT 'lftr',
    source_id text,
    kind text NOT NULL DEFAULT 'tile',
    tier text NOT NULL DEFAULT 'regional',
    properties jsonb NOT NULL DEFAULT '{}'::jsonb,
    geom geometry(Polygon, 4326) NOT NULL,
    label_point geometry(Point, 4326),
    bbox geometry(Polygon, 4326),
    generated_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS spatial_tiles_geom_gix ON {{SCHEMA}}.spatial_tiles USING gist (geom);
CREATE INDEX IF NOT EXISTS spatial_tiles_label_gix ON {{SCHEMA}}.spatial_tiles USING gist (label_point);
CREATE INDEX IF NOT EXISTS spatial_tiles_kind_idx ON {{SCHEMA}}.spatial_tiles (kind);
CREATE INDEX IF NOT EXISTS spatial_tiles_source_idx ON {{SCHEMA}}.spatial_tiles (source, source_id);
