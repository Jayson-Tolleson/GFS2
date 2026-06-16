from app.core.config import get_settings
from app.layers.contracts import LayerContract
from app.providers.gfs_ncss import get_gfs_provider
from app.providers.rtofs_ncep import get_rtofs_provider
from app.spatial.postgis_optional import postgis_status

BASE_BUDGET = {
    'global': {'clouds': 16, 'rain': 20, 'ocean': 18, 'bait': 12, 'boats': 6, 'lightning': 12, 'inland-water': 20, 'reports': 12},
    'regional': {'clouds': 32, 'rain': 40, 'ocean': 36, 'bait': 24, 'boats': 12, 'lightning': 24, 'inland-water': 60, 'reports': 24},
    'local': {'clouds': 56, 'rain': 72, 'ocean': 64, 'bait': 40, 'boats': 24, 'lightning': 50, 'inland-water': 120, 'reports': 40},
}


def layer_contracts() -> list[LayerContract]:
    settings = get_settings()
    return [
        LayerContract(id='clouds', label='Clouds', kind='field', source='gfs_ncss_atmosphere.cloud_density', depends_on=['atmosphere.field.patch'], stream_events=['atmosphere.field.patch'], renderer='CloudFieldLayer', budget={k: v['clouds'] for k, v in BASE_BUDGET.items()}, todo=['Real GFS NetCDF parsing']),
        LayerContract(id='rain', label='Rain', kind='field', source='gfs_ncss_atmosphere.rain_rate', depends_on=['atmosphere.field.patch'], stream_events=['atmosphere.field.patch'], renderer='RainFieldLayer', budget={k: v['rain'] for k, v in BASE_BUDGET.items()}, todo=['Real GFS NetCDF parsing']),
        LayerContract(id='ocean', label='Ocean', kind='field', source='rtofs_ncep_ocean.currents_sst', depends_on=['ocean.field.patch'], stream_events=['ocean.field.patch'], renderer='OceanFieldLayer', budget={k: v['ocean'] for k, v in BASE_BUDGET.items()}, todo=['Real RTOFS NetCDF parsing']),
        LayerContract(id='bait', label='Bait', kind='scalar_field', source='ocean_truth.bait_score', depends_on=['ocean.field.patch'], stream_events=['ocean.field.patch'], renderer='BaitFieldLayer', budget={k: v['bait'] for k, v in BASE_BUDGET.items()}, todo=['Future chlorophyll boost', 'Future depth-aware bait scoring']),
        LayerContract(id='boats', label='Boats', kind='entity', source='viewport+spatial_water+ocean_current', depends_on=['viewport-spatial', 'ocean.field.patch'], stream_events=['boats.patch'], renderer='BoatLayer', budget={k: v['boats'] for k, v in BASE_BUDGET.items()}, todo=['Replace mock generator with AIS/user vessel sources later']),
        LayerContract(id='inland-water', label='Inland Water', kind='spatial', source='usgs/postgis waterbodies', depends_on=['viewport-spatial.waterbodies'], stream_events=[], renderer='InlandWaterLayer', budget={k: v['inland-water'] for k, v in BASE_BUDGET.items()}, todo=['Live lake temperature later']),
        LayerContract(id='lightning', label='Lightning', kind='event', enabled=settings.lightning_enabled, source=f'{settings.lightning_provider}_lightning', depends_on=['lightning.flash'], stream_events=['lightning.flash'], renderer='LightningLayer', budget={k: v['lightning'] for k, v in BASE_BUDGET.items()}, degraded=not settings.lightning_enabled, todo=['Future GLM provider']),
        LayerContract(id='reports', label='Reports', kind='spatial_points', source='csv/postgis reports', depends_on=['viewport-spatial.reports'], stream_events=['reports.patch'], renderer='ReportLayer', budget={k: v['reports'] for k, v in BASE_BUDGET.items()}),
    ]


def layer_status() -> dict:
    return {
        'ok': True,
        'contract_version': 'lftr.layers.v1',
        'layers': [contract.model_dump(mode='json') for contract in layer_contracts()],
        'providers': {'gfs': get_gfs_provider().status().model_dump(mode='json'), 'rtofs': get_rtofs_provider().status().model_dump(mode='json')},
        'spatial': {'postgis': postgis_status()},
        'renderer_expectations': {'flow': 'snapshot -> stream -> field store -> target state -> animation loop -> morphing object pools', 'no_full_redraw': True},
    }
