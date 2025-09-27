import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
function Heatmap() {
  const mapRef = useRef(null);
  const [data, setData] = useState([]);
  const [submittedCount, setSubmittedCount] = useState(0);
  const searchLatRef = useRef(null);
  const searchLngRef = useRef(null);
  const searchMarkerRef = useRef(null);

  useEffect(() => {
    // Initialize the map directly since Leaflet is now properly imported
    initialize();

    return () => {
      // cleanup leaflet elements if any
      if (mapRef.current && mapRef.current.remove) {
        mapRef.current.remove();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function fetchData() {
    try {
      const res = await fetch('http://82.177.167.151:5001/heatmap/data');
      const json = await res.json();
      setData(json.data || []);
      setSubmittedCount(json.submitted || 0);
      return json.data || [];
    } catch (err) {
      console.error('Failed to fetch heatmap data', err);
      return [];
    }
  }

  async function initialize() {
    const heatmapData = await fetchData();

    // Create map
    mapRef.current = L.map('map').setView([20, 0], 2);

    // Add dark tiles (CartoDB Dark Matter)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
      maxZoom: 19
    }).addTo(mapRef.current);

    // Add markers
    addMarkers(heatmapData);
  }

  function addMarkers(points) {
    if (!mapRef.current) return;

    points.forEach(point => {
      const color = point.value > 100 ? 'red' :
                    point.value > 85 ? 'orange' :
                    point.value > 70 ? 'yellow' :
                    point.value > 50 ? 'green' : 'blue';

      const isSubmitted = point.is_submitted || false;
      // use a light stroke for contrast on dark backgrounds
      const markerOptions = {
        radius: isSubmitted ? 9 : 6,
        fillColor: color,
        color: '#ffffff',
        weight: isSubmitted ? 2.5 : 1.25,
        opacity: 1,
        fillOpacity: isSubmitted ? 0.95 : 0.9
      };

      const marker = L.circleMarker([point.lat, point.lng], markerOptions).addTo(mapRef.current);
      marker.bindPopup(`${point.value.toFixed(1)} dB<br/>Event: ${point.event}<br/>Device: ${point.device_id}<br/>Lat: ${point.lat}<br/>Lng: ${point.lng}<br/>Type: ${isSubmitted ? 'Submitted' : 'Generated'}<br/>Time: ${new Date(point.timestamp).toLocaleString()}`);
    });
  }

  function showError(msg) {
    const el = document.getElementById('searchError');
    if (el) el.textContent = msg;
  }

  function clearError() {
    showError('');
  }

  function searchLocation() {
    clearError();
    const lat = parseFloat(searchLatRef.current.value);
    const lng = parseFloat(searchLngRef.current.value);

    if (isNaN(lat) || isNaN(lng)) {
      showError('Please enter valid latitude and longitude values');
      return;
    }
    if (lat < -90 || lat > 90) { showError('Latitude must be between -90 and 90'); return; }
    if (lng < -180 || lng > 180) { showError('Longitude must be between -180 and 180'); return; }

    mapRef.current.setView([lat, lng], 10);
    if (searchMarkerRef.current) {
      searchMarkerRef.current.remove();
    }
    searchMarkerRef.current = L.marker([lat, lng]).addTo(mapRef.current).bindPopup(`<b>Search Location</b><br/>Lat: ${lat}<br/>Lng: ${lng}`).openPopup();
  }

  function findNearestDevice() {
    clearError();
    const lat = parseFloat(searchLatRef.current.value);
    const lng = parseFloat(searchLngRef.current.value);
    if (isNaN(lat) || isNaN(lng)) { showError('Please enter valid coordinates to find nearest device'); return; }

    let nearest = null;
    let minDistance = Infinity;
    data.forEach(point => {
      const distance = Math.sqrt(Math.pow(point.lat - lat, 2) + Math.pow(point.lng - lng, 2));
      if (distance < minDistance) { minDistance = distance; nearest = point; }
    });

    if (nearest) {
      mapRef.current.setView([nearest.lat, nearest.lng], 12);
      L.popup()
        .setLatLng([nearest.lat, nearest.lng])
        .setContent(`<b>Nearest Device</b><br/>Device: ${nearest.device_id}<br/>Noise: ${nearest.value.toFixed(1)} dB<br/>Distance: ${(minDistance * 111).toFixed(2)} km`)
        .openOn(mapRef.current);
    } else {
      showError('No devices found');
    }
  }

  async function refreshData() {
    // remove existing map markers and reload
    if (mapRef.current && mapRef.current.eachLayer) {
      mapRef.current.eachLayer(layer => {
        // keep tile layer but remove markers/circleMarkers
        if (layer && layer._latlng) {
          try { mapRef.current.removeLayer(layer); } catch (e) {}
        }
      });
    }
    const newData = await fetchData();
    addMarkers(newData);
  }

  return (
    <div style={{ padding: 20 }}>
      <h1 style={{ color: '#fff' }}>Device Noise Level Heatmap</h1>

      <div style={{ marginBottom: 10 }} className="search-container">
        <strong>Search Location:</strong>
        <input ref={searchLatRef} type="number" placeholder="Latitude" step="any" min="-90" max="90" style={{ width: 200, padding: 5, margin: '0 5px' }} />
        <input ref={searchLngRef} type="number" placeholder="Longitude" step="any" min="-180" max="180" style={{ width: 200, padding: 5, margin: '0 5px' }} />
        <button onClick={searchLocation} style={{ padding: '5px 10px', marginRight: 6 }}>Go to Location</button>
        <button onClick={findNearestDevice} style={{ padding: '5px 10px' }}>Find Nearest Device</button>
        <span id="searchError" style={{ color: 'red', fontSize: 12, marginLeft: 8 }}></span>
      </div>

      <div className="legend" style={{ background: '#0b1220', color: '#e6eef8', padding: 10, borderRadius: 6, boxShadow: '0 6px 20px rgba(0,0,0,0.6)', marginBottom: 10 }}>
        <strong>Decibel Levels:</strong>
        <span style={{ color: '#7dd3fc', marginLeft: 8 }}>30-50 dB (Quiet)</span> | <span style={{ color: '#34d399' }}>50-70 dB (Moderate)</span> | <span style={{ color: '#fbbf24' }}>70-85 dB (Loud)</span> | <span style={{ color: '#fb923c' }}>85-100 dB (Very Loud)</span> | <span style={{ color: '#f87171' }}>100+ dB (Noise Pollution)</span>
        <br />
        <strong>Data Sources:</strong>
        <span style={{ background: 'rgba(125,211,252,0.12)', padding: '2px 6px', marginLeft: 6, borderRadius: 3 }}>Generated Data</span> |
        <span style={{ background: 'rgba(248,113,113,0.12)', padding: '2px 6px', marginLeft: 6, borderRadius: 3 }}>Submitted Data</span>
        <br />
        <button onClick={refreshData} style={{ padding: '5px 10px', marginTop: 6 }}>Refresh Data</button>
        <span id="dataCount" style={{ marginLeft: 8 }}>Total: {data.length} points ({submittedCount} submitted)</span>
      </div>

      <div id="map" style={{ height: 600, width: '100%', borderRadius: 6, overflow: 'hidden', boxShadow: '0 8px 30px rgba(2,6,23,0.6)' }}></div>
      {/* Dark popup styling for Leaflet popups */}
      <style>{`
        .leaflet-popup-content-wrapper { background: #0b1220; color: #e6eef8; border-radius: 6px; box-shadow: 0 6px 18px rgba(0,0,0,0.6); }
        .leaflet-popup-content { margin: 8px 12px; }
        .leaflet-popup-tip { background: #0b1220; }
      `}</style>
    </div>
  );
}

export default Heatmap;
