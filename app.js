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

let stopRoutesIndex = {};

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

  buildStopRoutesIndex();
  renderStats();
  renderList(filterRoutes());
  buildAllRoutesLayer();
  buildStopsLayer();
}

function buildStopRoutesIndex() {
  stopRoutesIndex = {};
  for (const feature of allFeatures()) {
    const p = feature.properties;
    for (const stop of (p.stops || [])) {
      if (!stop.name) continue;
      const key = stop.name.trim().toLowerCase();
      if (!stopRoutesIndex[key]) {
        stopRoutesIndex[key] = [];
      }
      if (!stopRoutesIndex[key].some(r => r.id === p.id)) {
        stopRoutesIndex[key].push({
          id: p.id,
          code: p.code,
          kind: p.kind,
          origin: p.origin,
          destination: p.destination
        });
      }
    }
  }
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
    const iconClass = r.kind === 'metro' ? 'fa-train-subway' : 'fa-bus';
    div.innerHTML = `
      <div class="route-header-row">
        <div class="route-code"><i class="fa-solid ${iconClass}"></i> ${esc(r.code)}</div>
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

  // Render stops in timeline panel with transfer badges
  detailStops.innerHTML = props.stops.map(s => {
    const key = (s.name || '').trim().toLowerCase();
    const connCount = (stopRoutesIndex[key] || []).length;
    const transferBadge = connCount > 1 ? `<span class="transfer-badge-count" title="${connCount} connecting lines">${connCount} lines</span>` : '';
    return `
      <li data-seq="${s.sequence}" data-lat="${s.lat}" data-lng="${s.lng}">
        <span><strong>${esc(s.sequence)}.</strong> ${esc(s.name)}</span>
        ${transferBadge}
      </li>
    `;
  }).join('');

  // Keep route polyline illumination intact
  selectedLayer = L.geoJSON(feature, {
    style: {
      color: colorFor(props.kind),
      weight: 6,
      opacity: 0.95,
    },
  }).addTo(map);

  const stopMarkersMap = {};
  const totalStops = props.stops.length;

  if (showStopsEl.checked) {
    for (const s of props.stops) {
      if (s.lat == null || s.lng == null) continue;
      
      const isOrigin = (s.sequence === 1);
      const isDest = (s.sequence === totalStops);
      
      const radius = isOrigin || isDest ? 8 : 5;
      const strokeColor = isOrigin ? '#10b981' : (isDest ? '#ef4444' : '#ffffff');
      const fillColor = isOrigin ? '#10b981' : (isDest ? '#ef4444' : colorFor(props.kind));

      const m = L.circleMarker([s.lat, s.lng], {
        radius: radius,
        color: strokeColor,
        weight: isOrigin || isDest ? 3 : 2,
        fillColor: fillColor,
        fillOpacity: 1,
      });

      // Hover tooltip for sequence & stop name
      m.bindTooltip(
        `<strong>Stop ${s.sequence}/${totalStops}</strong>: ${esc(s.name)}`,
        { direction: 'top', offset: [0, -6], opacity: 0.9 }
      );

      // Interactive popup with connecting route transfer chips
      const key = (s.name || '').trim().toLowerCase();
      const connections = (stopRoutesIndex[key] || []).filter(r => r.id !== props.id);
      
      let transferHtml = '';
      if (connections.length > 0) {
        const chips = connections.slice(0, 10).map(c => `
          <span class="transfer-chip ${c.kind}" data-route-id="${esc(c.id)}" title="${esc(c.code)}: ${esc(c.origin)} → ${esc(c.destination)}">
            <i class="fa-solid ${c.kind === 'metro' ? 'fa-train-subway' : 'fa-bus'}"></i> ${esc(c.code)}
          </span>
        `).join('');
        const moreCount = connections.length > 10 ? ` <span style="font-size:0.7rem;color:var(--ink-secondary);">+${connections.length - 10} more</span>` : '';
        transferHtml = `
          <div class="transfer-header">
            <span><i class="fa-solid fa-code-branch" style="color:var(--accent-gold);"></i> Connecting Lines (${connections.length})</span>
          </div>
          <div class="transfer-chips">${chips}${moreCount}</div>
        `;
      } else {
        transferHtml = `<div style="font-size:0.75rem;color:var(--ink-secondary);margin-top:6px;">No other direct transfers at this stop</div>`;
      }

      const popupContent = document.createElement('div');
      popupContent.className = 'stop-popup';
      popupContent.innerHTML = `
        <div class="stop-popup-header">
          <span class="stop-seq-badge">Stop ${s.sequence} of ${totalStops}</span>
        </div>
        <div class="stop-popup-name">${esc(s.name)}</div>
        <div class="stop-popup-sub">
          <i class="fa-solid fa-route" style="color:var(--accent-gold);"></i> Route ${esc(props.code)}
        </div>
        ${transferHtml}
        <button class="btn-search-stop" data-stop-name="${esc(s.name)}">
          <i class="fa-solid fa-magnifying-glass"></i> Filter routes at this stop
        </button>
      `;

      popupContent.querySelectorAll('.transfer-chip').forEach(chip => {
        chip.addEventListener('click', (e) => {
          e.stopPropagation();
          const routeId = chip.dataset.routeId;
          if (routeId) selectRoute(routeId);
        });
      });

      popupContent.querySelector('.btn-search-stop').addEventListener('click', (e) => {
        e.stopPropagation();
        searchEl.value = s.name;
        clearSearchBtn.classList.remove('hidden');
        renderList(filterRoutes());
        map.closePopup();
      });

      m.bindPopup(popupContent);
      selectedLayer.addLayer(m);
      stopMarkersMap[s.sequence] = m;
    }
  }

  // Side panel timeline hover & click interactions
  detailStops.querySelectorAll('li').forEach(li => {
    const seq = parseInt(li.dataset.seq);
    const lat = parseFloat(li.dataset.lat);
    const lng = parseFloat(li.dataset.lng);

    li.addEventListener('mouseenter', () => {
      li.classList.add('active-stop');
      const m = stopMarkersMap[seq];
      if (m) {
        m.setStyle({ radius: 9, weight: 4 });
      }
    });

    li.addEventListener('mouseleave', () => {
      li.classList.remove('active-stop');
      const m = stopMarkersMap[seq];
      if (m) {
        const isOrigin = (seq === 1);
        const isDest = (seq === totalStops);
        m.setStyle({ radius: isOrigin || isDest ? 8 : 5, weight: isOrigin || isDest ? 3 : 2 });
      }
    });

    li.addEventListener('click', () => {
      if (!isNaN(lat) && !isNaN(lng)) {
        map.flyTo([lat, lng], 16, { duration: 1.0 });
        const m = stopMarkersMap[seq];
        if (m) m.openPopup();
      }
    });
  });

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
    const key = name.trim().toLowerCase();
    const connections = stopRoutesIndex[key] || [];

    const m = L.circleMarker([info.lat, info.lng], {
      radius: 3,
      color: 'transparent',
      fillColor: '#f59e0b',
      fillOpacity: 0.6,
    });

    m.bindTooltip(`<strong>${esc(name)}</strong> (${connections.length} routes)`, { direction: 'top', opacity: 0.9 });

    const popupDiv = document.createElement('div');
    popupDiv.className = 'stop-popup';
    popupDiv.innerHTML = `
      <div class="stop-popup-name">${esc(name)}</div>
      <div class="stop-popup-sub">
        <i class="fa-solid fa-location-dot" style="color:var(--accent-gold);"></i> ${connections.length} Connecting Lines
      </div>
      <div class="transfer-chips">
        ${connections.slice(0, 12).map(c => `
          <span class="transfer-chip ${c.kind}" data-route-id="${esc(c.id)}">
            <i class="fa-solid ${c.kind === 'metro' ? 'fa-train-subway' : 'fa-bus'}"></i> ${esc(c.code)}
          </span>
        `).join('')}
        ${connections.length > 12 ? `<span style="font-size:0.7rem;color:var(--ink-secondary);">+${connections.length - 12} more</span>` : ''}
      </div>
      <button class="btn-search-stop" style="margin-top:8px;">Filter routes at this stop</button>
    `;

    popupDiv.querySelectorAll('.transfer-chip').forEach(chip => {
      chip.addEventListener('click', (e) => {
        e.stopPropagation();
        const routeId = chip.dataset.routeId;
        if (routeId) selectRoute(routeId);
      });
    });

    popupDiv.querySelector('.btn-search-stop').addEventListener('click', (e) => {
      e.stopPropagation();
      searchEl.value = name;
      clearSearchBtn.classList.remove('hidden');
      renderList(filterRoutes());
      map.closePopup();
    });

    m.bindPopup(popupDiv);
    group.addLayer(m);
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
