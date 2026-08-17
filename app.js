const KIND_COLORS = {
  government: '#10b981',
  private: '#3b82f6',
  mini: '#a855f7',
  metro: '#ff4757',
};

// Basemap Tile Layers
const BASEMAPS = {
  dark: L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO',
    maxZoom: 19,
  }),
  voyager: L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO',
    maxZoom: 19,
  }),
  satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: '&copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    maxZoom: 18,
  }),
};

let currentBasemap = BASEMAPS.dark;
const map = L.map('map', { zoomControl: false }).setView([22.5726, 88.3639], 12);
currentBasemap.addTo(map);

// Custom Zoom Control position
L.control.zoom({ position: 'bottomright' }).addTo(map);

let routeIndex = [];
let routesGeoByKind = {};
let allRoutesLayer = null;
let selectedLayer = null;
let stopsLayer = null;
let selectedId = null;
let activeKindFilter = '';

const routeListEl = document.getElementById('routeList');
const searchEl = document.getElementById('search');
const clearSearchBtn = document.getElementById('clearSearch');
const kindFilterEl = document.getElementById('kindFilter');
const scopeFilterEl = document.getElementById('scopeFilter');
const showAllEl = document.getElementById('showAllRoutes');
const showStopsEl = document.getElementById('showStops');
const statsEl = document.getElementById('stats');
const detailPanel = document.getElementById('routeDetail');
const detailBadge = document.getElementById('detailBadge');
const detailTitle = document.getElementById('detailTitle');
const detailMeta = document.getElementById('detailMeta');
const detailStops = document.getElementById('detailStops');

// Show loading state in stats
statsEl.innerHTML = '<div style="grid-column:1/-1;text-align:center;color:var(--ink-secondary);padding:10px;">Loading Transit Network...</div>';

async function loadData() {
  const [indexRes, stopsRes, govRes, privRes, miniRes, metroRes] = await Promise.all([
    fetch('data/routes_index.json'),
    fetch('data/stops_geocoded.json'),
    fetch('data/routes_government.geojson'),
    fetch('data/routes_private.geojson'),
    fetch('data/routes_mini.geojson'),
    fetch('data/routes_metro.geojson'),
  ]);

  routeIndex = await indexRes.json();
  window.stopsGeocoded = await stopsRes.json();

  routesGeoByKind.government = await govRes.json();
  routesGeoByKind.private    = await privRes.json();
  routesGeoByKind.mini       = await miniRes.json();
  routesGeoByKind.metro      = await metroRes.json();

  renderStats();
  renderList(filterRoutes());
  buildAllRoutesLayer();
  buildStopsLayer();
}

function renderStats() {
  const uniqueCodes = new Set(routeIndex.map(r => r.code)).size;
  const geocodedStops = Object.keys(window.stopsGeocoded || {}).length;
  statsEl.innerHTML = `
    <div class="stat"><div class="num">${routeIndex.length.toLocaleString()}</div><div class="lbl">Routes</div></div>
    <div class="stat"><div class="num">${uniqueCodes.toLocaleString()}</div><div class="lbl">Bus Nos</div></div>
    <div class="stat"><div class="num">${geocodedStops.toLocaleString()}</div><div class="lbl">Stops</div></div>
  `;
}

function filterRoutes() {
  const q = searchEl.value.trim().toLowerCase();
  const kind = activeKindFilter || kindFilterEl.value;
  const scope = scopeFilterEl.value;
  return routeIndex.filter(r => {
    if (kind && r.kind !== kind) return false;
    if (scope && r.scope !== scope) return false;
    if (!q) return true;
    const hay = `${r.code} ${r.origin} ${r.destination} ${r.towards}`.toLowerCase();
    return hay.includes(q);
  });
}

function renderList(routes) {
  const frag = document.createDocumentFragment();
  const max = 400;
  const shown = routes.slice(0, max);
  
  if (routes.length === 0) {
    const empty = document.createElement('div');
    empty.style.padding = '20px';
    empty.style.textAlign = 'center';
    empty.style.color = 'var(--ink-secondary)';
    empty.innerHTML = '<i class="fa-solid fa-magnifying-glass" style="font-size:1.5rem;margin-bottom:8px;display:block;"></i> No matching routes found';
    routeListEl.innerHTML = '';
    routeListEl.appendChild(empty);
    return;
  }

  for (const r of shown) {
    const div = document.createElement('div');
    div.className = `route-item ${r.kind}` + (r.id === selectedId ? ' active' : '');
    div.dataset.id = r.id;
    const covPct = Math.round(r.coverage * 100);
    div.innerHTML = `
      <div class="route-header-row">
        <div class="route-code">${esc(r.code)}</div>
        <span class="badge ${r.kind}">${r.kind}</span>
      </div>
      <div class="route-path">${esc(r.origin)} <i class="fa-solid fa-arrow-right arrow"></i> ${esc(r.destination)}</div>
      <div class="route-meta">
        <span>${r.stop_count} stops · ${covPct}% mapped</span>
        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: ${covPct}%"></div></div>
      </div>
    `;
    div.addEventListener('click', () => selectRoute(r.id));
    frag.appendChild(div);
  }
  routeListEl.innerHTML = '';
  routeListEl.appendChild(frag);

  if (routes.length > max) {
    const note = document.createElement('div');
    note.style.padding = '10px';
    note.style.textAlign = 'center';
    note.style.fontSize = '0.75rem';
    note.style.color = 'var(--ink-secondary)';
    note.textContent = `Showing ${max} of ${routes.length} routes. Refine search for more.`;
    routeListEl.appendChild(note);
  }
}

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c =>
    ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function getFeature(id) {
  for (const fc of Object.values(routesGeoByKind)) {
    const f = fc.features.find(f => f.properties.id === id);
    if (f) return f;
  }
  return null;
}

function allFeatures() {
  return Object.values(routesGeoByKind).flatMap(fc => fc.features);
}

function colorFor(kind) {
  return KIND_COLORS[kind] || '#888';
}

function selectRoute(id) {
  selectedId = id;
  renderList(filterRoutes());

  if (selectedLayer) {
    map.removeLayer(selectedLayer);
    selectedLayer = null;
  }

  const feature = getFeature(id);
  if (!feature) return;

  const props = feature.properties;
  detailPanel.classList.remove('hidden');
  detailBadge.textContent = props.kind;
  detailBadge.className = `badge ${props.kind}`;
  detailTitle.textContent = `Route ${props.code}`;
  detailMeta.innerHTML = `
    <i class="fa-solid fa-route" style="color:var(--accent-gold);margin-right:4px;"></i>
    <strong>${esc(props.origin)}</strong> &rarr; <strong>${esc(props.destination)}</strong><br>
    Scope: <span style="text-transform:capitalize;">${props.scope}</span> &middot; 
    ${props.stop_count} stops (${props.geocoded_stops} mapped on map)
  `;

  detailStops.innerHTML = props.stops.map(s =>
    `<li data-lat="${s.lat}" data-lng="${s.lng}">
      <strong>${esc(s.sequence)}.</strong> ${esc(s.name)}
    </li>`
  ).join('');

  // Add click handler to fly to individual stop
  detailStops.querySelectorAll('li').forEach(li => {
    li.addEventListener('click', () => {
      const lat = parseFloat(li.dataset.lat);
      const lng = parseFloat(li.dataset.lng);
      if (!isNaN(lat) && !isNaN(lng)) {
        map.flyTo([lat, lng], 15, { duration: 1.2 });
      }
    });
  });

  selectedLayer = L.geoJSON(feature, {
    style: {
      color: colorFor(props.kind),
      weight: 6,
      opacity: 0.95,
    },
  }).addTo(map);

  if (showStopsEl.checked) {
    for (const s of props.stops) {
      const m = L.circleMarker([s.lat, s.lng], {
        radius: 6,
        color: '#ffffff',
        weight: 2,
        fillColor: colorFor(props.kind),
        fillOpacity: 1,
      }).bindPopup(`
        <div style="font-family:var(--font-body);padding:2px;">
          <strong style="font-size:0.95rem;color:#fff;">${esc(s.name)}</strong><br>
          <span style="font-size:0.78rem;color:var(--ink-secondary);">Stop ${s.sequence} &middot; Route ${esc(props.code)}</span>
        </div>
      `);
      selectedLayer.addLayer(m);
    }
  }

  map.fitBounds(selectedLayer.getBounds(), { padding: [50, 50] });
}

function buildAllRoutesLayer() {
  if (allRoutesLayer) map.removeLayer(allRoutesLayer);

  const combined = {
    type: 'FeatureCollection',
    features: allFeatures(),
  };

  allRoutesLayer = L.geoJSON(combined, {
    style: f => ({
      color: colorFor(f.properties.kind),
      weight: 2,
      opacity: 0.25,
    }),
    onEachFeature: (f, layer) => {
      layer.on('click', () => selectRoute(f.properties.id));
      layer.bindTooltip(
        `<strong>Route ${f.properties.code}</strong>: ${f.properties.origin} &rarr; ${f.properties.destination}`,
        { sticky: true }
      );
    },
  });
  if (showAllEl.checked) allRoutesLayer.addTo(map);
}

function buildStopsLayer() {
  if (stopsLayer) map.removeLayer(stopsLayer);
  const stops = window.stopsGeocoded || {};
  const group = L.layerGroup();
  for (const [name, info] of Object.entries(stops)) {
    L.circleMarker([info.lat, info.lng], {
      radius: 3,
      color: 'transparent',
      fillColor: '#f59e0b',
      fillOpacity: 0.5,
    }).bindPopup(`<strong style="color:#fff;">${esc(name)}</strong>`).addTo(group);
  }
  stopsLayer = group;
}

// Basemap Switcher Events
document.getElementById('btnMapDark').addEventListener('click', () => switchBasemap('dark'));
document.getElementById('btnMapVoyager').addEventListener('click', () => switchBasemap('voyager'));
document.getElementById('btnMapSatellite').addEventListener('click', () => switchBasemap('satellite'));

function switchBasemap(name) {
  map.removeLayer(currentBasemap);
  currentBasemap = BASEMAPS[name];
  currentBasemap.addTo(map);

  document.querySelectorAll('.map-btn').forEach(btn => btn.classList.remove('active'));
  if (name === 'dark') document.getElementById('btnMapDark').classList.add('active');
  if (name === 'voyager') document.getElementById('btnMapVoyager').classList.add('active');
  if (name === 'satellite') document.getElementById('btnMapSatellite').classList.add('active');
}

// Search Inputs & Clear Button
searchEl.addEventListener('input', () => {
  if (searchEl.value.length > 0) {
    clearSearchBtn.classList.remove('hidden');
  } else {
    clearSearchBtn.classList.add('hidden');
  }
  renderList(filterRoutes());
});

clearSearchBtn.addEventListener('click', () => {
  searchEl.value = '';
  clearSearchBtn.classList.add('hidden');
  renderList(filterRoutes());
});

// Shortcut '/' key to focus search
window.addEventListener('keydown', (e) => {
  if (e.key === '/' && document.activeElement !== searchEl) {
    e.preventDefault();
    searchEl.focus();
  }
});

// Filter Pills Events
document.querySelectorAll('#kindPills .pill').forEach(pill => {
  pill.addEventListener('click', () => {
    document.querySelectorAll('#kindPills .pill').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
    activeKindFilter = pill.dataset.kind;
    kindFilterEl.value = activeKindFilter;
    renderList(filterRoutes());
  });
});

kindFilterEl.addEventListener('change', () => {
  activeKindFilter = kindFilterEl.value;
  document.querySelectorAll('#kindPills .pill').forEach(p => {
    p.classList.toggle('active', p.dataset.kind === activeKindFilter);
  });
  renderList(filterRoutes());
});

scopeFilterEl.addEventListener('change', () => renderList(filterRoutes()));

showAllEl.addEventListener('change', () => {
  if (showAllEl.checked) {
    allRoutesLayer.addTo(map);
  } else if (allRoutesLayer) {
    map.removeLayer(allRoutesLayer);
  }
});

showStopsEl.addEventListener('change', () => {
  if (selectedId) selectRoute(selectedId);
});

// Locate Me Button
document.getElementById('btnLocateMe').addEventListener('click', () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((pos) => {
      const lat = pos.coords.latitude;
      const lng = pos.coords.longitude;
      map.flyTo([lat, lng], 14);
      L.marker([lat, lng]).addTo(map).bindPopup('<strong>Your Location</strong>').openPopup();
    }, () => {
      alert('Could not access your location');
    });
  }
});

// Mobile Drawer Toggle
const sidebar = document.getElementById('sidebar');
const btnToggleDrawer = document.getElementById('btnToggleDrawer');

btnToggleDrawer.addEventListener('click', () => {
  sidebar.classList.toggle('drawer-open');
});

document.getElementById('closeDetail').addEventListener('click', () => {
  detailPanel.classList.add('hidden');
});

loadData().catch(err => {
  statsEl.innerHTML = '';
  routeListEl.innerHTML = `<div style="padding:16px;color:#f87171">Failed to load data: ${esc(err.message)}</div>`;
});
