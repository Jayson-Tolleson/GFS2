import type { SceneGraph } from '../renderer/sceneGraph';

export function registercloudsLayer(graph: SceneGraph): void {
  graph.upsert({ id: 'mock-clouds', layer: 'clouds', kind: 'mock', data: { todo: 'replace clouds mock with live field truth rendering' } });
}
