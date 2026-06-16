const LAYERS = ['Clouds', 'Rain', 'Ocean', 'Bait', 'Boats', 'Inland Water', 'Lightning', 'Reports'];

export function renderLayerPills(): HTMLElement {
  const wrapper = document.createElement('div');
  wrapper.className = 'layer-pills';
  for (const label of LAYERS) {
    const pill = document.createElement('button');
    pill.className = 'layer-pill';
    pill.textContent = label;
    wrapper.appendChild(pill);
  }
  return wrapper;
}
