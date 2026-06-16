from app.fields.base import FieldPatch
from app.fields.encoders import encode_atmosphere_json_patch
from app.providers.gfs_ncss import get_gfs_provider
from app.providers.provider_status import ProviderStatus
from app.schemas.scene import BBox


class FieldTruthEngine:
    def atmosphere_frame(self, bbox: BBox):
        return get_gfs_provider().fetch_atmosphere(bbox)

    def atmosphere_patch(self, bbox: BBox, lod: int = 0) -> tuple[FieldPatch, ProviderStatus]:
        frame, status = self.atmosphere_frame(bbox)
        patch = encode_atmosphere_json_patch(frame, lod=lod)
        patch.payload["provider"] = status.model_dump(mode="json")
        patch.payload["metadata"] = frame.metadata
        return patch, status


def get_field_truth_engine() -> FieldTruthEngine:
    return FieldTruthEngine()
