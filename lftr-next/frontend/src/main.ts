import './styles/app.css';
import { fetchSceneFrame, fetchViewportSpatial } from './api/client';
import { openFieldStream } from './api/stream';
import { AnimationLoop } from './renderer/animationLoop';
import { FieldStore } from './fields/fieldStore';
import { createMap3DPlaceholder } from './renderer/map3d';
import { SceneGraph } from './renderer/sceneGraph';
import { ViewportController } from './renderer/viewportController';
import type { FieldPatch } from './types/field';
import type { ReportPoint, SpatialFeature } from './types/spatial';
import type { BoatEntity, LightningFlash } from './types/layers';
import { CloudFieldLayer } from './layers/cloudFieldLayer';
import { RainFieldLayer } from './layers/rainFieldLayer';
import { OceanFieldLayer } from './layers/oceanFieldLayer';
import { BaitFieldLayer } from './layers/baitFieldLayer';
import { BoatLayer } from './layers/boatLayer';
import { LightningLayer } from './layers/lightningLayer';
import { InlandWaterLayer } from './layers/inlandWaterLayer';
import { ReportLayer } from './layers/reportLayer';
import { renderLayerPills } from './ui/layerPills';
import { createIntelligencePane } from './ui/intelligencePane';
import { registercloudsLayer } from './layers/clouds';
import { registerrainLayer } from './layers/rain';
import { registeroceanLayer } from './layers/ocean';
import { registerbaitLayer } from './layers/bait';
import { registerboatsLayer } from './layers/boats';
import { registerinlandWaterLayer } from './layers/inlandWater';

const app = document.querySelector<HTMLDivElement>('#app')!;
const shell = document.createElement('main'); shell.className = 'app-shell'; shell.appendChild(createMap3DPlaceholder());
const visualRoot = document.createElement('div'); visualRoot.className = 'visual-root'; shell.appendChild(visualRoot);
const title = document.createElement('div'); title.className = 'glass-title'; title.textContent = 'LFTR Marine Intelligence Globe'; shell.append(title, renderLayerPills());
const pane = createIntelligencePane(); shell.appendChild(pane.element); app.appendChild(shell);

const graph = new SceneGraph(); const fields = new FieldStore(); const viewport = new ViewportController(); const loop = new AnimationLoop();
const clouds = new CloudFieldLayer(fields, visualRoot); const rain = new RainFieldLayer(fields, visualRoot); const ocean = new OceanFieldLayer(fields, visualRoot); const bait = new BaitFieldLayer(fields, visualRoot);
const boats = new BoatLayer(visualRoot); const lightning = new LightningLayer(visualRoot); const inlandWater = new InlandWaterLayer(visualRoot); const reports = new ReportLayer(visualRoot, (report) => pane.selectReport(report));
loop.add(clouds); loop.add(rain); loop.add(ocean); loop.add(bait); loop.add(boats); loop.add(lightning); loop.add(inlandWater); loop.add(reports); loop.start();

registercloudsLayer(graph); registerrainLayer(graph); registeroceanLayer(graph); registerbaitLayer(graph); registerboatsLayer(graph); registerinlandWaterLayer(graph);
pane.log(`SceneGraph initialized with ${graph.all().length} stable mock objects`);

viewport.onChange((bbox) => {
  fetchViewportSpatial(bbox).then((spatial) => {
    reports.setReports(spatial.reports); inlandWater.setWaterbodies(spatial.waterbodies ?? spatial.lakes);
    pane.renderReports(spatial.reports); pane.log(`Viewport spatial: ${spatial.reports.length} reports, ${(spatial.waterbodies ?? []).length} waterbodies`);
    const value = [bbox.west, bbox.south, bbox.east, bbox.north].join(',');
    fetch(`/gfs/api/layers/boats?bbox=${encodeURIComponent(value)}`).then((res) => res.json()).then((payload: { boats: BoatEntity[] }) => boats.setBoats(payload.boats ?? []));
  }).catch((error: Error) => pane.log(`Viewport spatial error: ${error.message}`));
});
viewport.updateFromMockCamera(); window.addEventListener('resize', () => viewport.updateFromMockCamera());

fetchSceneFrame().then((scene) => pane.log(`Loaded scene ${scene.scene_id}`)).catch((error: Error) => pane.log(`Scene error: ${error.message}`));
openFieldStream((event) => {
  if (event.type === 'atmosphere.field.patch' || event.type === 'ocean.field.patch') { fields.applyPatch(event.payload as unknown as FieldPatch); pane.log(`${event.type}: target patch stored`); return; }
  if (event.type === 'reports.patch') { const nextReports = (event.payload.reports as ReportPoint[]) ?? []; reports.setReports(nextReports); pane.renderReports(nextReports); }
  if (event.type === 'lightning.flash') lightning.addFlashes((event.payload.flashes as LightningFlash[]) ?? []);
  if (event.type === 'boats.patch') boats.setBoats((event.payload.boats as BoatEntity[]) ?? []);
  pane.log(event);
});
