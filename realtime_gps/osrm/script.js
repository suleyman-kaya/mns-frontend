document.addEventListener('DOMContentLoaded', () => {
  initMap();
  document.getElementById('calculate-route').addEventListener('click', calculateRoutes);
});

let map, marker, polylines = [], markers = [], routesData = [];

function initMap() {
  map = L.map('map').setView([39.925018, 32.836956], 8);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  marker = L.marker([39.925018, 32.836956], {
    icon: L.icon({
      iconUrl: 'car.png',
      iconSize: [64, 64],
      iconAnchor: [32, 64]
    })
  }).addTo(map);

  startTracking('http://localhost:5000/gps');
}

function getCoords(type) {
  return [
    parseFloat(document.getElementById(`${type}-lng`).value),
    parseFloat(document.getElementById(`${type}-lat`).value)
  ];
}

async function calculateRoutes() {
  try {
    const start = getCoords('start');
    const end = getCoords('end');
    const waypoints = document.getElementById('waypoints').value
      .split(';')
      .map(coord => coord.split(',').map(parseFloat).reverse());

    console.log('Start:', start);
    console.log('End:', end);
    console.log('Waypoints:', waypoints);

    const waypointCombinations = getCombinations(waypoints);
    console.log('Waypoint combinations:', waypointCombinations);

    const combinationsInfo = document.getElementById('combinations-info');
    combinationsInfo.textContent = `Toplam ${waypointCombinations.length} farklı rota kombinasyonu hesaplanıyor.`;

    clearMarkersAndPolylines();
    addMarkers(start, end, waypoints);

    routesData = await Promise.all(waypointCombinations.map(async combo => {
      try {
        return await calculateRoute([start, ...combo, end]);
      } catch (error) {
        console.error('Error calculating route:', error);
        return null;
      }
    }));

    console.log('Routes data:', routesData);

    routesData = routesData.filter(route => route !== null);
    
    if (routesData.length === 0) {
      throw new Error('Hiç geçerli rota bulunamadı');
    }

    routesData.sort((a, b) => a.energyConsumption - b.energyConsumption);
    showAlternativeRoutes();
  } catch (error) {
    console.error('calculateRoutes fonksiyonunda hata:', error);
    alert('Rota hesaplanırken bir hata oluştu: ' + error.message);
  }
}

async function calculateEnergyConsumption(route) {
  try {
    const response = await fetch('http://localhost:5000/calculateEnergyConsumption', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ route }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.energyConsumption;
  } catch (error) {
    console.error('Enerji tüketimi hesaplanırken bir hata oluştu:', error);
    throw error;
  }
}

function getCombinations(array) {
  const result = [];
  const f = (prefix = [], array) => {
    for (let i = 0; i < array.length; i++) {
      result.push([...prefix, array[i]]);
      f([...prefix, array[i]], array.slice(i + 1));
    }
  };
  f([], array);
  return result;
}

function clearMarkersAndPolylines() {
  markers.forEach(marker => map.removeLayer(marker));
  polylines.forEach(polyline => map.removeLayer(polyline));
  markers = [];
  polylines = [];
}

function addMarkers(start, end, waypoints) {
  addMarker(start.reverse(), 'Start');
  waypoints.forEach((waypoint, index) => addMarker(waypoint.slice().reverse(), (index + 1).toString()));
  addMarker(end.reverse(), 'End');
}

function addMarker(position, label) {
  const marker = L.marker(position, { title: label }).addTo(map);
  markers.push(marker);
}

async function calculateRoute(points) {
  try {
    console.log('Calculating route for points:', points);
    const url = `https://router.project-osrm.org/route/v1/driving/${points.map(p => p.join(',')).join(';')}?overview=full&geometries=geojson`;
    console.log('OSRM API URL:', url);

    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();

    if (data.routes && data.routes.length > 0) {
      const route = data.routes[0];
      console.log('Route data:', route);
      const energyConsumption = await calculateEnergyConsumption(route);
      return { route, energyConsumption };
    } else {
      throw new Error('No routes found in OSRM API response');
    }
  } catch (err) {
    console.error('Rota hesaplanırken bir hata oluştu:', err);
    throw err;
  }
}

function getColorForEnergy(energyConsumption, minEnergy, maxEnergy) {
  const hue = ((energyConsumption - minEnergy) / (maxEnergy - minEnergy)) * 120;
  return `hsl(${120 - hue}, 100%, 50%)`;
}

function showAlternativeRoutes() {
  const routeList = document.getElementById('route-list');
  routeList.innerHTML = '';

  const [minEnergy, maxEnergy] = [Math.min(...routesData.map(d => d.energyConsumption)), Math.max(...routesData.map(d => d.energyConsumption))];

  routesData.forEach(({ route, energyConsumption }, index) => {
    const color = getColorForEnergy(energyConsumption, minEnergy, maxEnergy);

    const weight = (index === 0) ? 9 : 3;

    const polyline = L.polyline(route.geometry.coordinates, {
      color: color,
      weight: weight
    }).addTo(map);
    polylines.push(polyline);

    const routeItem = document.createElement('li');
    routeItem.textContent = `Rota ${index + 1}: Mesafe: ${(route.distance / 1000).toFixed(2)} km - Enerji Tüketimi: ${energyConsumption.toFixed(2)}`;
    routeItem.style.color = color;
    routeItem.addEventListener('click', () => {
      map.fitBounds(polyline.getBounds());
    });
    routeList.appendChild(routeItem);
  });

  const combinationsInfo = document.getElementById('combinations-info');
  combinationsInfo.textContent = `${routesData.length} farklı rota hesaplandı ve sıralandı.`;
}

let lastFetchTime = 0;
const FETCH_INTERVAL = 2000; // 2 seconds

async function fetchGpsData(endpoint) {
  try {
    const response = await fetch(endpoint);
    const { latitude, longitude } = await response.json();
    const newPosition = [parseFloat(latitude), parseFloat(longitude)];

    marker.setLatLng(newPosition);
    
    console.log(`Latitude: ${latitude}, Longitude: ${longitude}`);
  } catch (error) {
    console.error('GPS verisi alınırken hata oluştu:', error);
  }
}

function startTracking(endpoint) {
  setInterval(() => fetchGpsData(endpoint), FETCH_INTERVAL);
}