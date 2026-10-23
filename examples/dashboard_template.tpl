<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root {
  --bg: #eef3f8;
  --card: #ffffff;
  --ink: #14213d;
  --muted: #5b677a;
  --line: #dbe4ee;
  --accent: #0f4c81;
  --accent-dark: #0b3d68;
  --soft: #f6f9fc;
}
* { box-sizing: border-box; }
html, body { height: 100%; }
body {
  margin: 0;
  overflow: hidden;
  background: var(--bg);
  color: var(--ink);
  font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
  line-height: 1.4;
}
button, select, input { font: inherit; }
button { cursor: pointer; }
a { color: var(--accent); }
.topbar {
  height: 64px;
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 0 16px;
  color: #fff;
  background: linear-gradient(120deg, #0b2545 0%, #123a67 58%, #1a5a86 100%);
  border-bottom: 1px solid rgba(255,255,255,.12);
}
.brand { display: flex; align-items: center; gap: 10px; min-width: 310px; }
.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  flex: none;
  font-weight: 800;
  font-size: .82rem;
  letter-spacing: .06em;
  background: rgba(255,255,255,.14);
  border: 1px solid rgba(255,255,255,.24);
}
.brand-copy { min-width: 0; }
.brand-title {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.brand-sub {
  margin-top: 2px;
  font-size: .72rem;
  color: #c9dcf0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.kpi-chips {
  margin-left: auto;
  display: flex;
  gap: 7px;
  min-width: 0;
  overflow: hidden;
}
.kpi-chip {
  flex: 0 0 auto;
  min-width: 86px;
  padding: 5px 9px;
  border-radius: 9px;
  background: rgba(255,255,255,.10);
  border: 1px solid rgba(255,255,255,.18);
}
.kpi-chip span {
  display: block;
  font-size: .61rem;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: #c9dcf0;
  white-space: nowrap;
}
.kpi-chip strong { font-size: .94rem; line-height: 1.3; }
.kpi-chip em { margin-left: 3px; font-style: normal; font-size: .68rem; color: #c9dcf0; }
.dashboard {
  height: calc(100vh - 64px);
  display: grid;
  grid-template-columns: 400px minmax(0, 1fr);
  min-height: 0;
}
.sidebar {
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: var(--card);
  border-right: 1px solid var(--line);
}
.tabs {
  display: flex;
  gap: 4px;
  padding: 7px 8px;
  border-bottom: 1px solid var(--line);
  background: #fbfdff;
}
.tab {
  flex: 1 1 0;
  min-width: 0;
  padding: 7px 4px;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  color: #475569;
  font-size: .76rem;
  font-weight: 600;
  white-space: nowrap;
}
.tab:hover { background: #eef5fc; }
.tab.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.tab-panels { position: relative; flex: 1; min-height: 0; }
.panel {
  position: absolute;
  inset: 0;
  display: none;
  flex-direction: column;
  min-height: 0;
  overflow: auto;
  padding: 14px;
}
.panel.active { display: flex; }
.panel-head { margin-bottom: 10px; }
.panel-head h2 { margin: 0 0 3px; font-size: 1.08rem; letter-spacing: -.01em; }
.panel-head p { margin: 0; color: var(--muted); font-size: .78rem; }
.panel-subtitle { margin: 16px 0 7px; font-size: .9rem; }
.layer-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.layer-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  min-height: 38px;
  padding: 7px 8px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  color: #334155;
  text-align: left;
  font-size: .75rem;
  line-height: 1.2;
}
.layer-btn:hover { background: #f5f9fd; border-color: #b8cbe0; }
.layer-btn.active {
  border-color: var(--accent);
  background: #edf5fd;
  box-shadow: inset 0 0 0 1px var(--accent);
  color: #0b3d68;
  font-weight: 700;
}
.layer-swatch {
  width: 22px;
  height: 10px;
  flex: none;
  border-radius: 999px;
  border: 1px solid rgba(15,23,42,.16);
}
.switch {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px 0 0;
  color: #334155;
  font-size: .8rem;
}
.switch input { width: 15px; height: 15px; accent-color: var(--accent); }
.active-layer {
  margin-top: 12px;
  padding: 10px 11px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--soft);
}
.active-layer-name { font-size: .85rem; font-weight: 700; }
.active-layer-help { margin-top: 3px; color: var(--muted); font-size: .75rem; }
.panel-note {
  margin-top: auto;
  padding-top: 12px;
  color: var(--muted);
  font-size: .73rem;
}
.chip-tabs { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 9px; }
.chip-tab {
  padding: 5px 8px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: #fff;
  color: #475569;
  font-size: .7rem;
  font-weight: 600;
}
.chip-tab:hover { background: #f1f7fd; }
.chip-tab.active { background: var(--accent); border-color: var(--accent); color: #fff; }
.chart-side-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: #fff;
}
.chart-side-card h3 { margin: 0 0 3px; font-size: .9rem; }
.caption { margin: 0 0 7px; color: var(--muted); font-size: .72rem; }
.chart-side-box { position: relative; flex: 1; min-height: 180px; }
.chart-side-box canvas { width: 100% !important; height: 100% !important; }
.chart-fallback {
  height: 100%;
  display: grid;
  place-items: center;
  padding: 16px;
  text-align: center;
  color: var(--muted);
  font-size: .8rem;
}
.table-controls { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.table-controls input { flex: 1 1 100%; min-width: 0; }
.table-controls select { flex: 0 0 auto; }
input[type="search"], select {
  padding: 7px 9px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #fff;
  color: var(--ink);
}
input[type="search"]:focus, select:focus { outline: 2px solid #bfdbfe; border-color: #60a5fa; }
.btn-primary { background: var(--accent); border: 1px solid var(--accent); color: #fff; border-radius: 8px; padding: 7px 10px; }
.btn-primary:hover { background: var(--accent-dark); }
button:not(.tab):not(.layer-btn):not(.chip-tab):not(.btn-primary) {
  padding: 7px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #fff;
  color: var(--ink);
}
button:not(.tab):not(.layer-btn):not(.chip-tab):not(.btn-primary):hover { background: #f1f5f9; }
button:disabled { opacity: .45; cursor: not-allowed; }
.table-scroll {
  flex: 1;
  min-height: 0;
  overflow: auto;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: #fff;
}
#panel-summary .table-scroll { flex: 0 0 auto; max-height: 34vh; }
.table-footer { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding-top: 8px; }
.muted { color: var(--muted); }
.small { font-size: .73rem; }
.data-table { width: 100%; border-collapse: collapse; font-size: .74rem; white-space: nowrap; }
.data-table th, .data-table td { padding: 6px 8px; border-bottom: 1px solid #eef2f7; text-align: left; }
.data-table th {
  position: sticky;
  top: 0;
  z-index: 2;
  background: #eef5fc;
  color: #334155;
  font-weight: 700;
}
.data-table tbody tr:hover { background: #f8fafc; }
.data-table td.num, .data-table th.num { text-align: right; font-variant-numeric: tabular-nums; }
.data-table th.sortable { cursor: pointer; user-select: none; }
.data-table th.sortable:hover { background: #e2eefb; }
.findings { margin: 0 0 4px; padding-left: 19px; font-size: .8rem; }
.findings li { margin: 0 0 9px; }
.method-text { color: #334155; font-size: .78rem; }
.method-text ul { margin: 0; padding-left: 18px; }
.method-text li { margin: 0 0 7px; }
code {
  padding: 1px 4px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: #f1f5f9;
  font-size: .9em;
}
.map-area { display: flex; flex-direction: column; min-width: 0; min-height: 0; background: #dfe7f0; }
.map-toolbar {
  min-height: 52px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 7px 12px;
  background: #fff;
  border-bottom: 1px solid var(--line);
}
.map-layer-title { min-width: 0; flex: 1; }
.map-layer-title strong { display: block; font-size: .86rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.map-layer-title span { display: block; color: var(--muted); font-size: .7rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.map-actions { display: flex; align-items: center; gap: 7px; flex: none; }
.map-actions select { max-width: 240px; }
.map-canvas { position: relative; flex: 1; min-height: 0; }
#map { position: absolute; inset: 0; background: #dfe7f0; }
.map-legend {
  position: absolute;
  right: 12px;
  bottom: 12px;
  z-index: 500;
  width: min(290px, 42vw);
  max-height: 48%;
  overflow: auto;
  padding: 9px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 9px;
  background: rgba(255,255,255,.96);
  box-shadow: 0 8px 22px rgba(15,23,42,.16);
  font-size: .72rem;
}
.legend-title { margin-bottom: 5px; font-weight: 700; color: #334155; }
.legend-item { display: flex; align-items: center; gap: 6px; margin: 3px 0; color: #475569; }
.swatch { width: 14px; height: 14px; flex: none; border: 1px solid rgba(15,23,42,.15); border-radius: 3px; }
.map-data-note {
  position: absolute;
  left: 50%;
  bottom: 9px;
  z-index: 500;
  transform: translateX(-50%);
  padding: 3px 8px;
  border-radius: 5px;
  background: rgba(255,255,255,.9);
  color: #526173;
  font-size: .66rem;
  white-space: nowrap;
}
.map-fallback {
  height: 100%;
  display: grid;
  place-items: center;
  padding: 24px;
  text-align: center;
  color: var(--muted);
  font-size: .9rem;
}
.leaflet-container { font-family: inherit; }
.leaflet-tooltip {
  padding: 8px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 9px;
  background: rgba(255,255,255,.98);
  box-shadow: 0 9px 24px rgba(15,23,42,.18);
}
.tip { min-width: 245px; font-size: .78rem; }
.tip strong { display: block; margin-bottom: 2px; font-size: .88rem; }
.tip table { width: 100%; border-collapse: collapse; margin-top: 4px; }
.tip td { padding: 1px 0; vertical-align: top; }
.tip td:first-child { padding-right: 11px; color: #64748b; }
@media (max-width: 1180px) {
  .kpi-chip:nth-child(n+7) { display: none; }
}
@media (max-width: 980px) {
  body { overflow: auto; }
  .topbar { height: auto; flex-wrap: wrap; padding: 9px 12px; }
  .brand { min-width: 0; width: 100%; }
  .kpi-chips { width: 100%; margin-left: 0; overflow-x: auto; padding-bottom: 2px; }
  .dashboard { display: block; height: auto; }
  .sidebar { border-right: 0; border-bottom: 1px solid var(--line); }
  .tab-panels { height: 62vh; }
  .map-area { height: 72vh; }
  .map-toolbar { flex-wrap: wrap; }
  .map-layer-title { flex-basis: 100%; }
  .map-actions { width: 100%; }
  .map-actions select { flex: 1; max-width: none; }
}
</style>
<style>
:root {
  --bg: #f5f5f7;
  --card: #ffffff;
  --ink: #1d1d1f;
  --muted: #6e6e73;
  --line: rgba(0, 0, 0, .08);
  --accent: #0071e3;
  --accent-dark: #0066cc;
  --soft: #f5f5f7;
}
body {
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", "Segoe UI", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
.topbar {
  height: 64px;
  padding: 0 24px;
  gap: 20px;
  color: var(--ink);
  background: rgba(255, 255, 255, .78);
  border-bottom: 1px solid rgba(0, 0, 0, .07);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  position: relative;
  z-index: 1000;
}
.brand { min-width: 340px; gap: 11px; }
.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background: #1d1d1f;
  border: 0;
  color: #fff;
  font-size: .68rem;
  font-weight: 700;
  letter-spacing: .02em;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .16);
}
.brand-title {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: -.015em;
  color: var(--ink);
}
.brand-sub {
  margin-top: 1px;
  font-size: 11.5px;
  color: var(--muted);
  letter-spacing: -.005em;
}
.kpi-chips { gap: 7px; }
.kpi-chip {
  min-width: 82px;
  padding: 5px 10px;
  border-radius: 11px;
  background: rgba(255, 255, 255, .86);
  border: 1px solid rgba(0, 0, 0, .07);
  box-shadow: 0 1px 2px rgba(0, 0, 0, .035);
}
.kpi-chip span {
  color: #86868b;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: .055em;
}
.kpi-chip strong { font-size: 14px; font-weight: 600; letter-spacing: -.01em; }
.kpi-chip em { color: #86868b; font-size: 10px; }
.dashboard {
  height: calc(100vh - 64px);
  padding: 14px 20px 20px;
  gap: 14px;
  grid-template-columns: 380px minmax(0, 1fr);
}
.sidebar {
  background: rgba(255, 255, 255, .82);
  border: 1px solid rgba(255, 255, 255, .85);
  border-radius: 22px;
  box-shadow: 0 18px 50px rgba(0, 0, 0, .07);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  overflow: hidden;
}
.tabs {
  margin: 12px 12px 0;
  padding: 3px;
  gap: 2px;
  background: #eeeeF1;
  border: 0;
  border-radius: 12px;
}
.tab {
  padding: 7px 4px;
  border: 0;
  border-radius: 9px;
  background: transparent;
  color: #6e6e73;
  font-size: 11.5px;
  font-weight: 500;
}
.tab:hover { background: transparent; color: var(--ink); }
.tab.active {
  background: #fff;
  color: var(--ink);
  border: 0;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, .12), 0 0 0 .5px rgba(0, 0, 0, .04);
}
.tab-panels { margin-top: 1px; }
.panel {
  padding: 18px;
  scrollbar-width: thin;
  scrollbar-color: #c7c7cc transparent;
}
.panel::-webkit-scrollbar { width: 8px; }
.panel::-webkit-scrollbar-thumb { background: #c7c7cc; border-radius: 8px; border: 2px solid transparent; background-clip: content-box; }
.panel-head { margin-bottom: 14px; }
.panel-head h2 {
  margin: 0 0 4px;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: -.03em;
}
.panel-head p { color: var(--muted); font-size: 12.5px; line-height: 1.45; }
.panel-subtitle { margin: 18px 0 8px; font-size: 13px; font-weight: 600; letter-spacing: -.01em; }
.layer-grid { gap: 8px; }
.layer-btn {
  min-height: 44px;
  padding: 9px 10px;
  gap: 8px;
  border: 1px solid rgba(0, 0, 0, .08);
  border-radius: 13px;
  background: #fff;
  color: #3a3a3c;
  font-size: 11.5px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .025);
  transition: border-color .18s ease, background .18s ease, box-shadow .18s ease;
}
.layer-btn:hover { background: #fafafa; border-color: rgba(0, 0, 0, .16); }
.layer-btn.active {
  border-color: rgba(0, 113, 227, .5);
  background: #f0f7ff;
  color: #0055b3;
  font-weight: 600;
  box-shadow: 0 0 0 3px rgba(0, 113, 227, .1);
}
.layer-swatch {
  width: 24px;
  height: 8px;
  border: 0;
  border-radius: 999px;
}
.switch {
  position: relative;
  gap: 10px;
  margin: 15px 0 0;
  color: #3a3a3c;
  font-size: 12.5px;
  user-select: none;
}
.switch input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
}
.switch-track {
  width: 34px;
  height: 20px;
  flex: none;
  border-radius: 999px;
  background: #d2d2d7;
  position: relative;
  transition: background .2s ease;
}
.switch-track::after {
  content: "";
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .22);
  transition: transform .2s ease;
}
.switch input:checked + .switch-track { background: #34c759; }
.switch input:checked + .switch-track::after { transform: translateX(14px); }
.switch input:focus-visible + .switch-track { outline: 3px solid rgba(0, 113, 227, .24); }
.active-layer {
  margin-top: 14px;
  padding: 12px 13px;
  border: 0;
  border-radius: 14px;
  background: var(--soft);
}
.active-layer-name { font-size: 13px; font-weight: 600; letter-spacing: -.01em; }
.active-layer-help { margin-top: 3px; color: var(--muted); font-size: 11.5px; line-height: 1.45; }
.panel-note { color: #86868b; font-size: 11.5px; line-height: 1.55; }
.chip-tabs { gap: 6px; margin-bottom: 11px; }
.chip-tab {
  padding: 6px 11px;
  border: 1px solid rgba(0, 0, 0, .08);
  border-radius: 999px;
  background: #fff;
  color: #6e6e73;
  font-size: 11.5px;
  font-weight: 500;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .025);
}
.chip-tab:hover { background: #fafafa; color: var(--ink); }
.chip-tab.active { background: #1d1d1f; border-color: #1d1d1f; color: #fff; }
.chart-side-card {
  padding: 14px;
  border: 1px solid rgba(0, 0, 0, .08);
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, .04);
}
.chart-side-card h3 { font-size: 15px; font-weight: 600; letter-spacing: -.015em; }
.caption { color: var(--muted); font-size: 11.5px; line-height: 1.45; }
.table-controls { gap: 7px; margin-bottom: 10px; }
input[type="search"], select {
  padding: 8px 10px;
  border: 1px solid rgba(0, 0, 0, .1);
  border-radius: 10px;
  background: var(--soft);
  color: var(--ink);
  font-size: 12.5px;
}
input[type="search"]:focus, select:focus {
  outline: 3px solid rgba(0, 113, 227, .18);
  border-color: var(--accent);
  background: #fff;
}
.btn-primary {
  padding: 8px 12px;
  border: 1px solid var(--accent);
  border-radius: 10px;
  background: var(--accent);
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 113, 227, .24);
}
.btn-primary:hover { background: var(--accent-dark); }
button:not(.tab):not(.layer-btn):not(.chip-tab):not(.btn-primary) {
  padding: 8px 11px;
  border: 1px solid rgba(0, 0, 0, .1);
  border-radius: 10px;
  background: #fff;
  color: var(--ink);
  font-size: 12px;
}
button:not(.tab):not(.layer-btn):not(.chip-tab):not(.btn-primary):hover { background: #f5f5f7; }
.table-scroll {
  border: 1px solid rgba(0, 0, 0, .07);
  border-radius: 14px;
}
.data-table { font-size: 11.5px; }
.data-table th, .data-table td { padding: 9px 10px; border-bottom: 1px solid rgba(0, 0, 0, .055); }
.data-table th {
  background: #f5f5f7;
  color: #6e6e73;
  font-weight: 600;
  letter-spacing: .005em;
}
.data-table tbody tr:hover { background: #fbfbfd; }
.data-table th.sortable:hover { background: #ececef; }
.table-footer { padding-top: 10px; }
.findings { padding-left: 20px; font-size: 12.5px; line-height: 1.5; }
.findings li { margin-bottom: 11px; }
.method-text { color: #3a3a3c; font-size: 12px; line-height: 1.55; }
.method-text li { margin-bottom: 8px; }
code {
  padding: 1px 5px;
  border: 0;
  border-radius: 5px;
  background: #f0f0f3;
  color: #1d1d1f;
  font-size: .92em;
}
.map-area {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, .85);
  border-radius: 22px;
  overflow: hidden;
  box-shadow: 0 18px 50px rgba(0, 0, 0, .08);
}
.map-toolbar {
  min-height: 60px;
  padding: 9px 14px;
  background: rgba(255, 255, 255, .82);
  border-bottom: 1px solid rgba(0, 0, 0, .07);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
}
.map-layer-title strong { font-size: 14px; font-weight: 600; letter-spacing: -.015em; }
.map-layer-title span { font-size: 11.5px; color: var(--muted); }
.map-actions { gap: 8px; }
.map-actions select { max-width: 210px; background-color: var(--soft); }
.map-canvas { background: #e9e9ee; }
#map { background: #e9e9ee; }
.map-legend {
  right: 14px;
  bottom: 14px;
  padding: 12px 13px;
  border: 1px solid rgba(255, 255, 255, .7);
  border-radius: 16px;
  background: rgba(255, 255, 255, .78);
  box-shadow: 0 12px 30px rgba(0, 0, 0, .12);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  font-size: 11.5px;
}
.legend-title { margin-bottom: 6px; font-size: 12px; font-weight: 600; color: var(--ink); }
.legend-item { margin: 4px 0; color: #3a3a3c; }
.swatch { width: 12px; height: 12px; border: 0; border-radius: 3px; }
.map-data-note {
  bottom: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, .72);
  color: #6e6e73;
  font-size: 10.5px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.leaflet-bar {
  border: 0 !important;
  border-radius: 11px !important;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(0, 0, 0, .16);
}
.leaflet-bar a {
  width: 32px !important;
  height: 32px !important;
  line-height: 32px !important;
  background: rgba(255, 255, 255, .92) !important;
  color: #1d1d1f !important;
  border-bottom: 1px solid rgba(0, 0, 0, .07) !important;
}
.leaflet-bar a:hover { background: #fff !important; }
.leaflet-control-attribution {
  padding: 1px 6px !important;
  border-radius: 6px 0 0 0;
  background: rgba(255, 255, 255, .7) !important;
  color: #86868b !important;
  font-size: 9px !important;
}
.leaflet-control-scale-line {
  border-color: #6e6e73 !important;
  color: #6e6e73 !important;
  background: rgba(255, 255, 255, .65) !important;
  font-size: 9px !important;
}
.leaflet-tooltip {
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, .8);
  border-radius: 14px;
  background: rgba(255, 255, 255, .94);
  box-shadow: 0 12px 32px rgba(0, 0, 0, .16);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
.tip { min-width: 250px; font-size: 11.5px; }
.tip strong { font-size: 13px; font-weight: 600; }
.tip td:first-child { color: #86868b; }
@media (max-width: 1180px) {
  .brand { min-width: 300px; }
  .kpi-chip:nth-child(n+7) { display: none; }
}
@media (max-width: 980px) {
  .topbar { padding: 10px 14px; }
  .dashboard { padding: 10px; gap: 10px; }
  .sidebar, .map-area { border-radius: 18px; }
  .panel { padding: 16px; }
  .map-toolbar { padding: 10px; }
  .map-data-note { display: none; }
}
</style>
</head>
<body>

<header class="topbar">
  <div class="brand">
    <div class="brand-mark">МГО</div>
    <div class="brand-copy">
      <div class="brand-title">{{TITLE}}</div>
      <div class="brand-sub">{{TERRITORY}} · {{BLOCKS_COUNT}} кварталов · данные обновлены {{LAST_MODIFIED}}</div>
    </div>
  </div>
  <div class="kpi-chips">{{KPI_CHIPS}}</div>
</header>

<main class="dashboard">
  <aside class="sidebar">
    <nav class="tabs" role="tablist" aria-label="Разделы дашборда">
      <button class="tab active" type="button" data-tab="layers">Слои</button>
      <button class="tab" type="button" data-tab="charts">Графики</button>
      <button class="tab" type="button" data-tab="table">Таблица</button>
      <button class="tab" type="button" data-tab="summary">Сводка</button>
      <button class="tab" type="button" data-tab="notes">Выводы</button>
    </nav>
    <div class="tab-panels">
      <section id="panel-layers" class="panel active">
        <div class="panel-head">
          <h2>Слои карты</h2>
          <p>Переключайте слой карты кнопкой или списком в верхней панели карты.</p>
        </div>
        <div id="layerList" class="layer-grid"></div>
        <label class="switch"><input id="hideEmpty" type="checkbox"><span class="switch-track"></span> Скрывать кварталы без значения</label>
        <div class="active-layer">
          <div id="sidebarLayerName" class="active-layer-name">Землепользование</div>
          <div id="sidebarLayerHelp" class="active-layer-help"></div>
        </div>
        <div class="panel-note">
          Цвет квартала соответствует выбранному показателю. Серый — нет значения.
          Наведите курсор на квартал, чтобы увидеть все показатели.
        </div>
      </section>

      <section id="panel-charts" class="panel">
        <div class="panel-head">
          <h2>Графики</h2>
          <p>Выберите график — он откроется в этой же панели без прокрутки страницы.</p>
        </div>
        <div id="chartTabs" class="chip-tabs"></div>
        <div class="chart-side-card">
          <h3 id="chartTitle"></h3>
          <p id="chartCaption" class="caption"></p>
          <div id="chartHolder" class="chart-side-box"><canvas id="chartMain"></canvas></div>
        </div>
      </section>

      <section id="panel-table" class="panel">
        <div class="panel-head">
          <h2>Все кварталы</h2>
          <p>Поиск, сортировка по столбцам и выгрузка CSV. Таблица прокручивается внутри панели.</p>
        </div>
        <div class="table-controls">
          <input id="tableSearch" type="search" placeholder="Поиск по кварталам, землепользованию, морфотипу...">
          <select id="pageSize" aria-label="Строк на странице">
            <option value="25" selected>25 строк</option>
            <option value="50">50 строк</option>
            <option value="100">100 строк</option>
            <option value="250">250 строк</option>
          </select>
          <button id="exportCsv" class="btn-primary" type="button">CSV</button>
        </div>
        <div class="table-scroll">
          <table id="blocksTable" class="data-table">
            <thead></thead>
            <tbody></tbody>
          </table>
        </div>
        <div class="table-footer">
          <span id="tableInfo" class="muted small"></span>
          <div>
            <button id="prevPage" type="button">Назад</button>
            <button id="nextPage" type="button">Вперёд</button>
          </div>
        </div>
      </section>

      <section id="panel-summary" class="panel">
        <div class="panel-head">
          <h2>Сводка показателей</h2>
          <p>Среднее, медиана, квартили, диапазон, кластеры Spacematrix и использованные файлы.</p>
        </div>
        <h3 class="panel-subtitle">Все рассчитанные показатели</h3>
        <div class="table-scroll">{{SUMMARY_TABLE}}</div>
        <h3 class="panel-subtitle">Кластеры Spacematrix</h3>
        <div class="table-scroll">{{CLUSTER_TABLE}}</div>
        <h3 class="panel-subtitle">Паспорт источников</h3>
        <div class="table-scroll">{{PROVENANCE_TABLE}}</div>
        <h3 class="panel-subtitle">Источники и файлы</h3>
        <p class="small muted">
          Связей «{{SERVICE_LABEL}} — квартал»: {{LINKS_COUNT}}; суммарная распределённая ёмкость:
          {{LINKS_VALUE}} {{SERVICE_UNIT}}. Страница собрана из сохранённых файлов папки
          <code>output</code>; показатели не пересчитывались.
        </p>
        <div class="table-scroll">{{SOURCES_TABLE}}</div>
      </section>

      <section id="panel-notes" class="panel">
        <div class="panel-head">
          <h2>Краткие выводы</h2>
          <p>Автоматические выводы по сохранённым результатам. Население приведено к официальному итогу, остальные показатели — модельные оценки.</p>
        </div>
        <ul class="findings">{{CONCLUSIONS_HTML}}</ul>
        <h3 class="panel-subtitle">Методика и единицы</h3>
        <div class="method-text">
          <ul>
            <li><code>FSI</code> = общая площадь застройки / площадь квартала.</li>
            <li><code>GSI</code> = площадь застройки / площадь квартала, 0–1.</li>
            <li><code>MXI</code> = жилая площадь / общая площадь застройки, 0–1.</li>
            <li><code>L</code> = общая площадь застройки / площадь застройки, этажей.</li>
            <li><code>OSR</code> = (площадь квартала − площадь застройки) / общая площадь застройки.</li>
            <li><code>Обеспеченность</code> — конкурентная обеспеченность сервисом, доля 0–1.</li>
            <li><code>Доступность</code> — средневзвешенное по площади время в пути, минуты.</li>
            <li><code>Жилая классификация</code> — OSM-здания <code>building=yes</code> в жилой зоне с этажностью 2+ считаются жилыми.</li>
            <li><code>Ёмкость и спрос</code> — в единицах «{{SERVICE_UNIT}}».</li>
          </ul>
        </div>
        <h3 class="panel-subtitle">Ограничения</h3>
        <div class="method-text">
          <ul>
            <li>Базовые геоданные — OpenStreetMap; полнота слоёв зависит от карты.</li>
            <li>Microsoft Building Footprints дополняет контуры зданий, но не содержит этажности и назначения.</li>
            <li>Официальные выгрузки подключаются из <code>better_data</code>; без них используются OSM-оценки.</li>
            <li>Население калибруется по официальной численности округа, а площади и ёмкость сервисов остаются модельными.</li>
            <li>Правило <code>building=yes</code> применяется только при известной этажности 2+; малоэтажные и бесэтажные объекты без жилых тегов остаются нежилыми.</li>
            <li>Категория «Не определено» — отсутствие тега землепользования, а не отсутствие функции.</li>
            <li>Обеспеченность учитывает конкуренцию кварталов и порог доступности.</li>
            <li>Учитывается только автомобильный граф; нулевые пары исключены из статистики времени.</li>
          </ul>
        </div>
        <h3 class="panel-subtitle">Данные и инструменты</h3>
        <div class="method-text">
          OpenStreetMap contributors; Microsoft GlobalMLBuildingFootprints; официальные выгрузки
          Магнитогорского городского округа и Челябинской области; BlocksNet 1.0.0a9; IduEdu 0.4.1; OSMnx.
          Страница собрана {{GENERATED_AT}} из сохранённых файлов папки <code>output</code>.
        </div>
      </section>
    </div>
  </aside>

  <section class="map-area">
    <div class="map-toolbar">
      <div class="map-layer-title">
        <strong id="mapLayerName">Землепользование</strong>
        <span id="mapLayerHelp">Тип функционального использования квартала</span>
      </div>
      <div class="map-actions">
        <select id="metricSelect" aria-label="Слой карты"></select>
        <select id="basemapSelect" aria-label="Подложка карты">
          <option value="osm">OpenStreetMap</option>
          <option value="light" selected>Светлая подложка</option>
          <option value="dark">Тёмная подложка</option>
        </select>
        <button id="resetView" type="button">Сброс вида</button>
      </div>
    </div>
    <div class="map-canvas">
      <div id="map" role="application" aria-label="Интерактивная карта кварталов"></div>
      <div id="mapLegend" class="map-legend"></div>
      <div class="map-data-note">Данные: OpenStreetMap · Microsoft · официальные выгрузки · BlocksNet</div>
    </div>
  </section>
</main>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script>
const DATA = {{DATA_JSON}};
const BLOCKS = {{BLOCKS_JSON}};

const nf0 = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 });
const nf1 = new Intl.NumberFormat('ru-RU', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const nf2 = new Intl.NumberFormat('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const nf3 = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 3 });

function fmt(value, digits) {
  if (value === null || value === undefined || value === '' || Number.isNaN(Number(value))) return '—';
  const number = Number(value);
  if (digits === 0) return nf0.format(number);
  if (digits === 1) return nf1.format(number);
  if (digits === 2) return nf2.format(number);
  return nf3.format(number);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, function (char) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char];
  });
}

function previewGradient(metric) {
  const colors = metric.kind === 'category'
    ? Object.keys(metric.colors).map(function (key) { return metric.colors[key]; }).slice(0, 5)
    : metric.classes.colors;
  return 'linear-gradient(90deg,' + colors.join(',') + ')';
}

function tooltipHtml(props) {
  const rows = [
    ['Землепользование', props.land_use_label],
    ['Население', fmt(props.population, 0) + ' чел.'],
    ['Ёмкость', fmt(props.capacity, 0) + ' ' + DATA.serviceUnit],
    ['Спрос', fmt(props.demand, 0) + ' ' + DATA.serviceUnit],
    ['Обеспеченность', fmt(props.provision_strong, 2)],
    ['FSI', fmt(props.fsi, 3)],
    ['GSI', fmt(props.gsi, 3)],
    ['MXI', fmt(props.mxi, 3)],
    ['L', fmt(props.l, 2) + ' этажей'],
    ['Доступность', fmt(props.area_accessibility, 1) + ' мин'],
    ['Spacematrix', props.morphotype_spacematrix || 'Нет данных'],
    ['Strelka', props.morphotype_strelka || 'Нет данных'],
  ];
  return '<div class="tip"><strong>Квартал ' + escapeHtml(props.block_id) + '</strong>' +
    '<table>' + rows.map(function (row) {
      return '<tr><td>' + escapeHtml(row[0]) + '</td><td>' + escapeHtml(row[1]) + '</td></tr>';
    }).join('') + '</table></div>';
}

const mapState = {
  currentMetricIndex: 0,
  currentBasemap: 'light',
  hideEmpty: false
};

let mapInstance = null;
let geojsonLayer = null;
let chartInstance = null;
let activeChartKey = null;

function currentMetric() {
  return DATA.map.metrics[mapState.currentMetricIndex];
}

function metricValue(metric, props) {
  const value = props[metric.key];
  if (metric.kind === 'category') {
    return value === null || value === undefined || value === '' ? 'Нет данных' : String(value);
  }
  if (value === null || value === undefined || value === '') return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function colorFor(metric, value) {
  if (metric.kind === 'category') return metric.colors[value] || '#d9d9d9';
  if (value === null) return '#e5e7eb';
  const breaks = metric.classes.breaks;
  const colors = metric.classes.colors;
  for (let i = 0; i < breaks.length - 1; i += 1) {
    const right = breaks[i + 1];
    const isLast = i === breaks.length - 2;
    if (value >= breaks[i] && (value < right || (isLast && value <= right))) {
      return colors[i] || colors[colors.length - 1];
    }
  }
  return value < breaks[0] ? colors[0] : colors[colors.length - 1];
}

function isMissing(metric, value) {
  return metric.kind === 'category' ? value === 'Нет данных' : value === null;
}

function styleFeature(feature) {
  const metric = currentMetric();
  const value = metricValue(metric, feature.properties);
  if (mapState.hideEmpty && isMissing(metric, value)) {
    return { fillColor: '#cbd5e1', fillOpacity: 0.05, color: '#cbd5e1', weight: 0.3, opacity: 0.35 };
  }
  return {
    fillColor: colorFor(metric, value),
    fillOpacity: 0.84,
    color: '#ffffff',
    weight: 0.6,
    opacity: 0.94
  };
}

function renderLegend(metric) {
  const legend = document.getElementById('mapLegend');
  let items = [];
  if (metric.kind === 'category') {
    items = Object.keys(metric.colors).map(function (label) {
      return [label, metric.colors[label]];
    });
  } else {
    items = metric.classes.labels.map(function (label, index) {
      return [label, metric.classes.colors[index]];
    });
  }
  legend.innerHTML = '<div class="legend-title">' + escapeHtml(metric.label) + '</div>' +
    items.map(function (item) {
      return '<div class="legend-item"><span class="swatch" style="background:' +
        escapeHtml(item[1]) + '"></span>' + escapeHtml(item[0]) + '</div>';
    }).join('');
}

function renderLayerList() {
  const list = document.getElementById('layerList');
  list.innerHTML = DATA.map.metrics.map(function (metric, index) {
    return '<button type="button" class="layer-btn' + (index === mapState.currentMetricIndex ? ' active' : '') +
      '" data-index="' + index + '" title="' + escapeHtml(metric.label) + '">' +
      '<span class="layer-swatch" style="background:' + previewGradient(metric) + '"></span>' +
      '<span>' + escapeHtml(metric.shortLabel || metric.label) + '</span></button>';
  }).join('');
  list.querySelectorAll('.layer-btn').forEach(function (button) {
    button.addEventListener('click', function () {
      setMetric(Number(button.dataset.index));
    });
  });
}

function setMetric(index) {
  mapState.currentMetricIndex = index;
  const metric = currentMetric();
  const metricSelect = document.getElementById('metricSelect');
  if (metricSelect) metricSelect.value = String(index);
  document.querySelectorAll('.layer-btn').forEach(function (button) {
    button.classList.toggle('active', Number(button.dataset.index) === index);
  });
  document.getElementById('mapLayerName').textContent = metric.label;
  document.getElementById('mapLayerHelp').textContent = metric.help;
  document.getElementById('sidebarLayerName').textContent = metric.label;
  document.getElementById('sidebarLayerHelp').textContent = metric.help;
  renderLegend(metric);
  if (geojsonLayer) geojsonLayer.setStyle(styleFeature);
}

function onEachFeature(feature, layer) {
  const html = tooltipHtml(feature.properties);
  layer.bindTooltip(html, { sticky: true, direction: 'top', opacity: 0.97, className: 'block-tooltip' });
  layer.bindPopup(html, { maxWidth: 400 });
  layer.on('mouseover', function () {
    layer.setStyle({ weight: 2.4, color: '#0f172a', fillOpacity: 0.94 });
    layer.bringToFront();
  });
  layer.on('mouseout', function () {
    layer.setStyle(styleFeature(feature));
  });
}

function initMap() {
  mapInstance = L.map('map', { preferCanvas: true, zoomControl: true });
  const baseLayers = {
    osm: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }),
    light: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19,
      maxNativeZoom: 16,
      attribution: 'Tiles &copy; Esri'
    }),
    dark: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19,
      maxNativeZoom: 16,
      attribution: 'Tiles &copy; Esri'
    })
  };
  mapInstance.addLayer(baseLayers[mapState.currentBasemap]);
  L.control.scale({ imperial: false }).addTo(mapInstance);

  geojsonLayer = L.geoJSON(BLOCKS, {
    style: styleFeature,
    onEachFeature: onEachFeature
  }).addTo(mapInstance);
  mapInstance.fitBounds(geojsonLayer.getBounds(), { padding: [18, 18] });

  document.getElementById('basemapSelect').addEventListener('change', function (event) {
    mapInstance.removeLayer(baseLayers[mapState.currentBasemap]);
    mapState.currentBasemap = event.target.value;
    mapInstance.addLayer(baseLayers[mapState.currentBasemap]);
  });
  document.getElementById('resetView').addEventListener('click', function () {
    mapInstance.fitBounds(geojsonLayer.getBounds(), { padding: [18, 18] });
  });
  document.getElementById('hideEmpty').addEventListener('change', function (event) {
    mapState.hideEmpty = event.target.checked;
    geojsonLayer.setStyle(styleFeature);
  });

  setMetric(mapState.currentMetricIndex);
  setTimeout(function () { mapInstance.invalidateSize(); }, 120);
}

function chartValueLabel(spec, value) {
  if (['шт.', 'пар', 'чел.', 'га'].indexOf(spec.unit) !== -1) return fmt(value, 0) + ' ' + spec.unit;
  return fmt(value, 1) + ' ' + spec.unit;
}

function buildChart(canvas, spec) {
  if (spec.type === 'doughnut') {
    return new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: spec.labels,
        datasets: [{
          label: spec.datasetLabel,
          data: spec.values,
          backgroundColor: spec.colors,
          borderColor: '#ffffff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '56%',
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 11, font: { size: 10 } } },
          tooltip: {
            callbacks: {
              label: function (context) {
                const total = context.dataset.data.reduce(function (sum, value) { return sum + Number(value); }, 0);
                const share = total ? (Number(context.parsed) / total * 100).toFixed(1) : '0.0';
                return context.label + ': ' + chartValueLabel(spec, context.parsed) + ' (' + share + '%)';
              }
            }
          }
        }
      }
    });
  }

  const horizontal = Boolean(spec.horizontal);
  const valueAxis = horizontal ? 'x' : 'y';
  const categoryAxis = horizontal ? 'y' : 'x';
  const scales = {};
  scales[valueAxis] = {
    beginAtZero: true,
    grid: { color: '#eef2f7' },
    title: { display: true, text: spec.unit, color: '#64748b', font: { size: 10 } },
    ticks: {
      precision: 0,
      font: { size: 10 },
      callback: function (value) { return fmt(value, 0); }
    }
  };
  scales[categoryAxis] = {
    grid: { display: false },
    ticks: { autoSkip: false, font: { size: 9 }, maxRotation: 55, minRotation: 0 }
  };

  return new Chart(canvas, {
    type: 'bar',
    data: {
      labels: spec.labels,
      datasets: [{
        label: spec.datasetLabel,
        data: spec.values,
        backgroundColor: spec.colors,
        borderColor: spec.colors,
        borderWidth: 0,
        borderRadius: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: horizontal ? 'y' : 'x',
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function (context) {
              const value = horizontal ? context.parsed.x : context.parsed.y;
              return spec.datasetLabel + ': ' + chartValueLabel(spec, value);
            }
          }
        }
      },
      scales: scales
    }
  });
}

function renderChartTabs() {
  const tabs = document.getElementById('chartTabs');
  tabs.innerHTML = Object.keys(DATA.charts).map(function (key) {
    const spec = DATA.charts[key];
    return '<button type="button" class="chip-tab" data-key="' + key + '">' +
      escapeHtml(spec.shortLabel || spec.title) + '</button>';
  }).join('');
  tabs.querySelectorAll('.chip-tab').forEach(function (button) {
    button.addEventListener('click', function () {
      showChart(button.dataset.key);
    });
  });
}

function showChart(key) {
  activeChartKey = key;
  const spec = DATA.charts[key];
  document.querySelectorAll('.chip-tab').forEach(function (button) {
    button.classList.toggle('active', button.dataset.key === key);
  });
  document.getElementById('chartTitle').textContent = spec.title;
  document.getElementById('chartCaption').textContent = spec.caption || '';
  const holder = document.getElementById('chartHolder');
  if (typeof Chart === 'undefined') {
    holder.innerHTML = '<div class="chart-fallback">Библиотека Chart.js не загрузилась. Проверьте подключение к интернету.</div>';
    return;
  }
  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }
  holder.innerHTML = '<canvas id="chartMain"></canvas>';
  chartInstance = buildChart(document.getElementById('chartMain'), spec);
  setTimeout(function () {
    if (chartInstance) chartInstance.resize();
  }, 40);
}

function initCharts() {
  renderChartTabs();
  if (typeof Chart === 'undefined') {
    document.getElementById('chartHolder').innerHTML =
      '<div class="chart-fallback">Библиотека Chart.js не загрузилась. Проверьте подключение к интернету.</div>';
    return;
  }
  const keys = Object.keys(DATA.charts);
  if (keys.length) showChart(keys[0]);
}

const tableState = {
  page: 1,
  pageSize: 25,
  query: '',
  sortIndex: 0,
  sortDir: 'asc'
};

function initTable() {
  const columns = DATA.table.columns;
  const thead = document.querySelector('#blocksTable thead');
  const tbody = document.querySelector('#blocksTable tbody');
  const search = document.getElementById('tableSearch');
  const pageSize = document.getElementById('pageSize');
  const prevPage = document.getElementById('prevPage');
  const nextPage = document.getElementById('nextPage');
  const tableInfo = document.getElementById('tableInfo');
  const exportButton = document.getElementById('exportCsv');

  function filterRows() {
    const query = tableState.query.trim().toLowerCase();
    let rows = DATA.table.rows;
    if (query) {
      rows = rows.filter(function (row) {
        return row.some(function (value) {
          return String(value === null || value === undefined ? '' : value).toLowerCase().indexOf(query) !== -1;
        });
      });
    }
    const column = columns[tableState.sortIndex];
    rows = rows.slice().sort(function (a, b) {
      const left = a[tableState.sortIndex];
      const right = b[tableState.sortIndex];
      if (column.type === 'number') {
        const leftNumber = left === null || left === undefined || left === '' ? null : Number(left);
        const rightNumber = right === null || right === undefined || right === '' ? null : Number(right);
        if (leftNumber === null && rightNumber === null) return 0;
        if (leftNumber === null) return 1;
        if (rightNumber === null) return -1;
        return tableState.sortDir === 'asc' ? leftNumber - rightNumber : rightNumber - leftNumber;
      }
      const leftText = String(left === null || left === undefined ? '' : left);
      const rightText = String(right === null || right === undefined ? '' : right);
      const result = leftText.localeCompare(rightText, 'ru');
      return tableState.sortDir === 'asc' ? result : -result;
    });
    return rows;
  }

  function formatCell(value, column) {
    if (value === null || value === undefined || value === '') return '—';
    if (column.type === 'number') return fmt(value, column.digits);
    return escapeHtml(String(value));
  }

  function renderHeader() {
    thead.innerHTML = '<tr>' + columns.map(function (column, index) {
      const sorted = index === tableState.sortIndex;
      const marker = sorted ? (tableState.sortDir === 'asc' ? ' ↑' : ' ↓') : '';
      return '<th class="sortable' + (column.type === 'number' ? ' num' : '') + '" data-index="' +
        index + '">' + escapeHtml(column.label) + marker + '</th>';
    }).join('') + '</tr>';
    thead.querySelectorAll('th').forEach(function (header) {
      header.addEventListener('click', function () {
        const index = Number(header.dataset.index);
        if (index === tableState.sortIndex) {
          tableState.sortDir = tableState.sortDir === 'asc' ? 'desc' : 'asc';
        } else {
          tableState.sortIndex = index;
          tableState.sortDir = 'asc';
        }
        tableState.page = 1;
        render();
      });
    });
  }

  function render() {
    renderHeader();
    const rows = filterRows();
    const pages = Math.max(1, Math.ceil(rows.length / tableState.pageSize));
    tableState.page = Math.min(tableState.page, pages);
    const start = (tableState.page - 1) * tableState.pageSize;
    const pageRows = rows.slice(start, start + tableState.pageSize);

    tbody.innerHTML = pageRows.map(function (row) {
      return '<tr>' + row.map(function (value, index) {
        const column = columns[index];
        return '<td class="' + (column.type === 'number' ? 'num' : '') + '">' +
          formatCell(value, column) + '</td>';
      }).join('') + '</tr>';
    }).join('');

    const first = rows.length ? start + 1 : 0;
    const last = Math.min(start + tableState.pageSize, rows.length);
    tableInfo.textContent = 'Показано ' + first + '–' + last + ' из ' + rows.length;
    prevPage.disabled = tableState.page <= 1;
    nextPage.disabled = tableState.page >= pages;
  }

  function csvCell(value, column) {
    if (value === null || value === undefined) return '';
    const text = column.type === 'number' ? String(value).replace('.', ',') : String(value);
    return '"' + text.replace(/"/g, '""') + '"';
  }

  exportButton.addEventListener('click', function () {
    const rows = filterRows();
    const lines = [columns.map(function (column) { return csvCell(column.label, { type: 'text' }); }).join(';')];
    rows.forEach(function (row) {
      lines.push(row.map(function (value, index) { return csvCell(value, columns[index]); }).join(';'));
    });
    const blob = new Blob(['\ufeff' + lines.join('\r\n')], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'blocks_indicators.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
  });

  search.addEventListener('input', function () {
    tableState.query = search.value;
    tableState.page = 1;
    render();
  });
  pageSize.addEventListener('change', function () {
    tableState.pageSize = Number(pageSize.value);
    tableState.page = 1;
    render();
  });
  prevPage.addEventListener('click', function () {
    tableState.page = Math.max(1, tableState.page - 1);
    render();
  });
  nextPage.addEventListener('click', function () {
    tableState.page += 1;
    render();
  });

  render();
}

function activateTab(name) {
  document.querySelectorAll('.tab').forEach(function (button) {
    button.classList.toggle('active', button.dataset.tab === name);
  });
  document.querySelectorAll('.panel').forEach(function (panel) {
    panel.classList.toggle('active', panel.id === 'panel-' + name);
  });
  if (name === 'charts') {
    if (!activeChartKey) initCharts();
    else setTimeout(function () { if (chartInstance) chartInstance.resize(); }, 50);
  }
}

function initTabs() {
  document.querySelectorAll('.tab').forEach(function (button) {
    button.addEventListener('click', function () {
      activateTab(button.dataset.tab);
    });
  });
}

function initLayerControls() {
  const metricSelect = document.getElementById('metricSelect');
  DATA.map.metrics.forEach(function (metric, index) {
    const option = document.createElement('option');
    option.value = String(index);
    option.textContent = metric.label;
    metricSelect.appendChild(option);
  });
  metricSelect.addEventListener('change', function () {
    setMetric(Number(metricSelect.value));
  });
  renderLayerList();
  setMetric(0);
}

initTabs();
initLayerControls();
initTable();
if (typeof L === 'undefined') {
  document.getElementById('map').innerHTML =
    '<div class="map-fallback">Библиотека Leaflet не загрузилась. Карта доступна при подключении к интернету; таблицы и графики работают независимо.</div>';
} else {
  initMap();
}
window.addEventListener('resize', function () {
  if (mapInstance) mapInstance.invalidateSize();
  if (chartInstance) chartInstance.resize();
});
</script>
</body>
</html>
