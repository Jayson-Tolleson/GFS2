import type { SceneGraph } from '../renderer/sceneGraph';

export function registerrainLayer(graph: SceneGraph): void {
  graph.upsert({ id: 'mock-rain', layer: 'rain', kind: 'mock', data: { todo: 'replace rain mock with live field truth rendering' } });
}
