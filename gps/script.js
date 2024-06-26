document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const apiKey = urlParams.get('api');

  if (apiKey) {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap`;
    document.head.appendChild(script);
  } else {
    console.error('API anahtarı URL parametrelerinde bulunamadı.');
  }

  document.getElementById('calculate-route').addEventListener('click', calculateRoutes);
});

let map;
let directionsService;
let directionsRenderer;
let marker;
let polylines = [];
let markers = [];
let routesData = [];

function initMap() {
  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer();
  
  const startCoords = getCoords('start');
  const mapOptions = {
    zoom: 8,
    center: startCoords
  };
  map = new google.maps.Map(document.getElementById('map'), mapOptions);
  
  marker = new google.maps.Marker({
    position: { lat: 39.925018, lng: 32.836956 },
    map: map,
    icon: {
      url: 'car.png',
      scaledSize: new google.maps.Size(64, 64)
    }
  });
  directionsRenderer.setMap(map);
  startTracking('http://localhost:5000/gps');
}

function getCoords(type) {
  const lat = parseFloat(document.getElementById(`${type}-lat`).value);
  const lng = parseFloat(document.getElementById(`${type}-lng`).value);
  return new google.maps.LatLng(lat, lng);
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

  clearMarkers(); // Önceki markerları temizle
  clearPolylines(); // Eski rotaları temizle

  addMarker(start, 'Start');
  waypoints.forEach((waypoint, index) => addMarker(waypoint.location, (index + 1).toString()));
  addMarker(end, 'End');

  routesData = [];

  for (const waypointSet of waypointCombinations) {
    const request = {
      origin: start,
      destination: end,
      waypoints: waypointSet,
      travelMode: google.maps.TravelMode.DRIVING,
      provideRouteAlternatives: false
    };

    const result = await directionsService.route(request).catch(err => console.error('Rota hesaplanırken bir hata oluştu:', err));
    if (result && result.routes && result.routes.length > 0) {
      const route = result.routes[0];
      const energyConsumption = await calculateEnergyConsumption(route);
      routesData.push({ route, energyConsumption });
    }
  }

  if (routesData.length === waypointCombinations.length) {
    routesData.sort((a, b) => a.energyConsumption - b.energyConsumption);
    showAlternativeRoutes();
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

function clearMarkers() {
  markers.forEach(marker => marker.setMap(null));
  markers = [];
}

function clearPolylines() {
  polylines.forEach(polyline => polyline.setMap(null));
  polylines = [];
}

function addMarker(position, label) {
  const marker = new google.maps.Marker({
    position,
    map,
    label,
  });
  markers.push(marker);
}

async function calculateEnergyConsumption(route) {
  try {
    const response = await fetch('http://localhost:5000/calculateEnergyConsumption', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ route: route }),
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
  const minEnergy = Math.min(...routesData.map(data => data.energyConsumption));
  const maxEnergy = Math.max(...routesData.map(data => data.energyConsumption));

  routesData.forEach((data, index) => {
    const route = data.route;
    const energyConsumption = data.energyConsumption;
    const color = getColorForEnergy(energyConsumption, minEnergy, maxEnergy);

    const polylineOptions = {
      strokeColor: color,
      strokeWeight: 6,
      zIndex: 1
    };

    const polyline = new google.maps.Polyline(polylineOptions);
    polyline.setPath(route.overview_path);
    polyline.setMap(map);
    polylines.push(polyline);

    const routeList = document.getElementById('route-list');
    const routeItem = document.createElement('li');
    routeItem.textContent = `Rota ${index + 1}: ${route.summary} - Enerji Tüketimi: ${energyConsumption.toFixed(2)}`;
    routeItem.style.color = color;
    routeItem.addEventListener('click', () => directionsRenderer.setDirections({ routes: [route] }));
    routeList.appendChild(routeItem);
  });
}

async function fetchGpsData(endpoint) {
  try {
    const response = await fetch(endpoint);
    const data = await response.json();
    const newPosition = new google.maps.LatLng(parseFloat(data.latitude), parseFloat(data.longitude));

    marker.setPosition(newPosition);

    if (!marker.getMap()) {
      marker.setMap(map);
    }

    map.setCenter(newPosition);
    console.log(`Latitude: ${data.latitude}, Longitude: ${data.longitude}`);
  } catch (error) {
    console.error('GPS verisi alınırken hata oluştu:', error);
  }
}

function startTracking(endpoint) {
  fetchGpsData(endpoint);
  setInterval(() => fetchGpsData(endpoint), 2000);
}
