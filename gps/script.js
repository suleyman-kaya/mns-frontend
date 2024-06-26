document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const apiKey = urlParams.get('api');

  if (apiKey) {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
  } else {
    console.error('API anahtarı URL parametrelerinde bulunamadı.');
  }

  document.getElementById('calculate-route').addEventListener('click', calculateRoutes);
});

let map, directionsService, directionsRenderer, marker, polylines = [], markers = [], routesData = [];

function initMap() {
  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer();
  
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 8,
    center: getCoords('start')
  });
  
  marker = new google.maps.Marker({
    position: { lat: 39.925018, lng: 32.836956 },
    map,
    icon: {
      url: 'car.png',
      scaledSize: new google.maps.Size(64, 64)
    }
  });
  directionsRenderer.setMap(map);
  startTracking('http://localhost:5000/gps');
}

function getCoords(type) {
  return new google.maps.LatLng(
    parseFloat(document.getElementById(`${type}-lat`).value),
    parseFloat(document.getElementById(`${type}-lng`).value)
  );
}

async function calculateRoutes() {
  const start = getCoords('start');
  const end = getCoords('end');
  const waypoints = document.getElementById('waypoints').value
    .split(';')
    .map(coord => {
      const [lat, lng] = coord.split(',').map(parseFloat);
      return { location: new google.maps.LatLng(lat, lng), stopover: true };
    });

  const waypointCombinations = getCombinations(waypoints);

  // Kombinasyon bilgisini güncelle
  const combinationsInfo = document.getElementById('combinations-info');
  combinationsInfo.textContent = `Toplam ${waypointCombinations.length} farklı rota kombinasyonu hesaplanıyor.`;

  clearMarkersAndPolylines();
  addMarkers(start, end, waypoints);

  routesData = await Promise.all(waypointCombinations.map(calculateRoute));
  routesData.sort((a, b) => a.energyConsumption - b.energyConsumption);
  showAlternativeRoutes();
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
  markers.forEach(marker => marker.setMap(null));
  polylines.forEach(polyline => polyline.setMap(null));
  markers = [];
  polylines = [];
}

function addMarkers(start, end, waypoints) {
  addMarker(start, 'Start');
  waypoints.forEach((waypoint, index) => addMarker(waypoint.location, (index + 1).toString()));
  addMarker(end, 'End');
}

function addMarker(position, label) {
  markers.push(new google.maps.Marker({ position, map, label }));
}

async function calculateRoute(waypointSet) {
  const request = {
    origin: getCoords('start'),
    destination: getCoords('end'),
    waypoints: waypointSet,
    travelMode: google.maps.TravelMode.DRIVING,
    provideRouteAlternatives: false
  };

  try {
    const result = await directionsService.route(request);
    if (result.routes && result.routes.length > 0) {
      const route = result.routes[0];
      const energyConsumption = await calculateEnergyConsumption(route);
      return { route, energyConsumption };
    }
  } catch (err) {
    console.error('Rota hesaplanırken bir hata oluştu:', err);
  }
}

async function calculateEnergyConsumption(route) {
  try {
    const response = await fetch('http://localhost:5000/calculateEnergyConsumption', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ route }),
    });
    const data = await response.json();
    return data.energyConsumption;
  } catch (error) {
    console.error('Enerji tüketimi hesaplanırken bir hata oluştu:', error);
  }
}

function getColorForEnergy(energyConsumption, minEnergy, maxEnergy) {
  const hue = ((energyConsumption - minEnergy) / (maxEnergy - minEnergy)) * 120;
  return `hsl(${120 - hue}, 100%, 50%)`;
}

function showAlternativeRoutes() {
  const routeList = document.getElementById('route-list');
  routeList.innerHTML = '';  // Clear previous routes

  const [minEnergy, maxEnergy] = [Math.min(...routesData.map(d => d.energyConsumption)), Math.max(...routesData.map(d => d.energyConsumption))];

  routesData.forEach(({ route, energyConsumption }, index) => {
    const color = getColorForEnergy(energyConsumption, minEnergy, maxEnergy);

    const polyline = new google.maps.Polyline({
      path: route.overview_path,
      strokeColor: color,
      strokeWeight: 6,
      map
    });
    polylines.push(polyline);

    const routeItem = document.createElement('li');
    routeItem.textContent = `Rota ${index + 1}: ${route.summary} - Enerji Tüketimi: ${energyConsumption.toFixed(2)}`;
    routeItem.style.color = color;
    routeItem.addEventListener('click', () => directionsRenderer.setDirections({ routes: [route] }));
    routeList.appendChild(routeItem);
  });

  // Hesaplama tamamlandığında bilgiyi güncelle
  const combinationsInfo = document.getElementById('combinations-info');
  combinationsInfo.textContent = `${routesData.length} farklı rota hesaplandı ve sıralandı.`;
}

let lastFetchTime = 0;
const FETCH_INTERVAL = 2000; // 2 seconds

async function fetchGpsData(endpoint) {
  const now = Date.now();
  if (now - lastFetchTime < FETCH_INTERVAL) return;
  lastFetchTime = now;

  try {
    const response = await fetch(endpoint);
    const { latitude, longitude } = await response.json();
    const newPosition = new google.maps.LatLng(parseFloat(latitude), parseFloat(longitude));

    marker.setPosition(newPosition);
    if (!marker.getMap()) marker.setMap(map);
    map.setCenter(newPosition);
    console.log(`Latitude: ${latitude}, Longitude: ${longitude}`);
  } catch (error) {
    console.error('GPS verisi alınırken hata oluştu:', error);
  }
}

function startTracking(endpoint) {
  setInterval(() => fetchGpsData(endpoint), FETCH_INTERVAL);
}