import type { ReportPoint } from '../types/spatial';
import type { FieldStreamEvent } from '../types/stream';

export function createIntelligencePane(): {
  element: HTMLElement;
  log: (event: FieldStreamEvent | string) => void;
  renderReports: (reports: ReportPoint[]) => void;
  selectReport: (report: ReportPoint) => void;
} {
  const element = document.createElement('aside');
  element.className = 'intelligence-pane';
  element.innerHTML = '<h2>Field Debug</h2><section class="selected-report"></section><section class="report-list"><h3>Reports</h3><ul></ul></section><ol></ol>';
  const selected = element.querySelector<HTMLElement>('.selected-report')!;
  const reportList = element.querySelector<HTMLUListElement>('.report-list ul')!;
  const list = element.querySelector<HTMLOListElement>('ol')!;
  return {
    element,
    log(event) {
      const item = document.createElement('li');
      item.textContent = typeof event === 'string' ? event : `${event.receivedAt} ${event.type}`;
      list.prepend(item);
      while (list.children.length > 12) list.lastElementChild?.remove();
    },
    renderReports(reports) {
      reportList.replaceChildren(...reports.map((report) => {
        const item = document.createElement('li');
        item.className = 'glowing-report';
        item.textContent = `${report.title}: ${report.summary}`;
        return item;
      }));
    },
    selectReport(report) {
      selected.innerHTML = `<h3>${report.title}</h3><p>${report.summary}</p><small>${report.observed_at} · ${report.latitude.toFixed(3)}, ${report.longitude.toFixed(3)}</small>`;
    },
  };
}
