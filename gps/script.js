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

  document.getElementById('calculate-route').addEventListener('click', calculateRoute);
});

let map;
let directionsService;
let directionsRenderer;
let marker;
let polylines = []; // Polyline'ları saklamak için dizi

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
  calculateRoute();
  startTracking('http://localhost:5000/gps');
}

function getCoords(type) {
  const lat = parseFloat(document.getElementById(`${type}-lat`).value);
  const lng = parseFloat(document.getElementById(`${type}-lng`).value);
  return new google.maps.LatLng(lat, lng);
}

function calculateRoute() {
  const start = getCoords('start');
  const end = getCoords('end');
  const request = {
    origin: start,
    destination: end,
    travelMode: google.maps.TravelMode.DRIVING,
    provideRouteAlternatives: true
  };

  directionsService.route(request, (result, status) => {
    if (status == google.maps.DirectionsStatus.OK) {
      clearPolylines(); // Eski rotaları temizle
      directionsRenderer.setDirections(result);
      console.log(`Alınabilecek toplam rota sayısı: ${result.routes.length}`);
      document.getElementById('route-count').textContent = `Toplam Rota Sayısı: ${result.routes.length}`;
      showAlternativeRoutes(result);
    } else {
      alert(`Rota hesaplanırken bir hata oluştu: ${status}`);
    }
  });
}

function clearPolylines() {
  polylines.forEach(polyline => polyline.setMap(null)); // Haritadan polyline'ları kaldır
  polylines = []; // Polyline dizisini temizle
}

function calculateEnergyConsumption(route) {
  let distance = 0;
  let elevationGain = 0;

  for (const leg of route.legs) {
    distance += leg.distance.value;

    for (const step of leg.steps) {
      if (step.elevation) {
        const elevationDiff = step.elevation.endLocation.lng - step.elevation.startLocation.lng;
        if (elevationDiff > 0) {
          elevationGain += elevationDiff;
        }
      }
    }
  }

  return distance * 0.001 + elevationGain * 0.01;
}

function getColorForEnergy(energyConsumption, minEnergy, maxEnergy) {
  const hue = ((energyConsumption - minEnergy) / (maxEnergy - minEnergy)) * 120;
  return `hsl(${120 - hue}, 100%, 50%)`;
}

function showAlternativeRoutes(result) {
  const routes = result.routes;
  let minEnergy = Infinity;
  let maxEnergy = 0;

  routes.forEach(route => {
    const energyConsumption = calculateEnergyConsumption(route);
    minEnergy = Math.min(minEnergy, energyConsumption);
    maxEnergy = Math.max(maxEnergy, energyConsumption);
  });

  const routeList = document.getElementById('route-list');
  routeList.innerHTML = ''; // Eski rota listesini temizle

  const numRoutesToShow = Math.min(routes.length, 5);
  routes.slice(0, numRoutesToShow).forEach((route, index) => {
    const routeItem = document.createElement('li');
    const energyConsumption = calculateEnergyConsumption(route);

    let color = getColorForEnergy(energyConsumption, minEnergy, maxEnergy);
    if (routes.length === 1) {
      color = 'green';
    } else if (routes.length === 2) {
      color = (energyConsumption === minEnergy) ? 'green' : 'red';
    }

    console.log(`Rota ${index + 1} enerji tüketimi: ${energyConsumption.toFixed(2)} birim`);

    const polylineOptions = {
      strokeColor: color,
      strokeWeight: 6,
      zIndex: 1
    };
    const polyline = new google.maps.Polyline(polylineOptions);
    polyline.setPath(route.overview_path);
    polyline.setMap(map);
    polylines.push(polyline); // Polyline'ı diziye ekle

    routeItem.textContent = `Rota ${index + 1}: ${route.summary}`;
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