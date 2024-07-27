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

let map, directionsService, directionsRenderer, marker, infoWindow, polylines = [], markers = [], routesData = [];

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

  infoWindow = new google.maps.InfoWindow({
    content: '<div id="info-content">Yükleniyor...</div>'
  });

  infoWindow.open(map, marker);

  directionsRenderer.setMap(map);
  startTracking();

  marker.addListener('click', () => { infoWindow.open(map, marker); });
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

  // Enerji tüketimine göre rota verilerini ters sırala (en az olan en üstte olacak)
  routesData.sort((a, b) => b.energyConsumption - a.energyConsumption);

  // En az ve en çok enerji tüketimini bul
  const [minEnergy, maxEnergy] = [Math.min(...routesData.map(d => d.energyConsumption)), Math.max(...routesData.map(d => d.energyConsumption))];

  routesData.forEach(({ route, energyConsumption }, index) => {
    const color = getColorForEnergy(energyConsumption, minEnergy, maxEnergy);

    // Polyline oluştururken enerji tüketimi en az olan rota için daha kalın bir çizgi kullan
    const strokeWeight = (index === routesData.length - 1) ? 18 : 6;  // İlk rota için kalınlığı artır

    const polyline = new google.maps.Polyline({
      path: route.overview_path,
      strokeColor: color,
      strokeWeight: strokeWeight,
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

async function fetchData(endpoint) {
  try {
    const response = await fetch(`http://localhost:5000${endpoint}`);
    return await response.json();
  } catch (error) {
    console.error(`Veri alınırken hata oluştu (${endpoint}):`, error);
    return null;
  }
}

let prevBatteryVoltage = null;
let prevBatteryCurrent = null;
let prevTotalJoulesUsed = null;

async function updateVehicleData() {
  const gpsData = await fetchData('/gps');
  const batteryVoltage = await fetchData('/batteryVoltage');
  const batteryCurrent = await fetchData('/batteryCurrent');
  const totalJoulesUsed = await fetchData('/totalJoulesUsed');
  const lastCalculatedGPSspeed = await fetchData('/lastCalculatedGPSspeed');

  if (gpsData) {
    const newPosition = new google.maps.LatLng(parseFloat(gpsData.latitude), parseFloat(gpsData.longitude));
    marker.setPosition(newPosition);
    if (!marker.getMap()) marker.setMap(map);
  }

  function getColorStyle(current, previous) {
    if (previous === null) return '';
    return current > previous ? 'color: green;' : 'color: red;';
  }

  function formatValue(value, unit) {
    return value ? value.toFixed(2) + ' ' + unit : 'N/A';
  }

  const voltageStyle = getColorStyle(batteryVoltage?.value, prevBatteryVoltage);
  const currentStyle = getColorStyle(batteryCurrent?.value, prevBatteryCurrent);
  const joulesStyle = getColorStyle(totalJoulesUsed?.value, prevTotalJoulesUsed);

  const infoContent = `
    <div style="background-color: white; color: Black; font-size: 18px;font-weight: bold;">
      <p style="${voltageStyle}">Pil Voltajı: ${formatValue(batteryVoltage?.value, 'V')}</p>
      <p style="${currentStyle}">Pil Akımı: ${formatValue(batteryCurrent?.value, 'A')}</p>
      <p style="${joulesStyle}">Toplam Kullanılan Enerji: ${formatValue(totalJoulesUsed?.value, 'J')}</p>
      <p>Son Hesaplanan GPS Hızı: ${formatValue(lastCalculatedGPSspeed?.value, 'km/s')}</p>
    </div>
  `;

  document.getElementById('info-content').innerHTML = infoContent;

  // Önceki değerleri güncelle
  prevBatteryVoltage = batteryVoltage?.value ?? prevBatteryVoltage;
  prevBatteryCurrent = batteryCurrent?.value ?? prevBatteryCurrent;
  prevTotalJoulesUsed = totalJoulesUsed?.value ?? prevTotalJoulesUsed;
}

function startTracking() {
  setInterval(updateVehicleData, FETCH_INTERVAL);
}
