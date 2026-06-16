import csv
from pathlib import Path
from app.schemas.scene import BBox
from app.spatial.base import ReportPoint

EXAMPLE_REPORTS = """id,title,lat,lon,observed_at,summary
report-port-everglades,Bait flicker off Port Everglades,26.091,-80.116,2026-06-16T00:00:00Z,Small bait pods near inlet edge
report-key-largo,Rain shelf near Key Largo,25.095,-80.438,2026-06-16T00:10:00Z,Light rain band drifting northeast
report-bimini,Current rip east of Bimini,25.728,-79.298,2026-06-16T00:20:00Z,Visible rip line with scattered birds
"""


def ensure_example_reports(path: Path) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(EXAMPLE_REPORTS, encoding="utf-8")


def load_reports(path: Path) -> list[ReportPoint]:
    ensure_example_reports(path)
    reports: list[ReportPoint] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            reports.append(
                ReportPoint(
                    id=row["id"],
                    title=row["title"],
                    latitude=float(row["lat"]),
                    longitude=float(row["lon"]),
                    observed_at=row["observed_at"],
                    summary=row["summary"],
                )
            )
    return reports


def filter_reports_by_bbox(reports: list[ReportPoint], bbox: BBox) -> list[ReportPoint]:
    return [report for report in reports if bbox.west <= report.longitude <= bbox.east and bbox.south <= report.latitude <= bbox.north]
