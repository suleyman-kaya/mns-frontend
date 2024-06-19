let map;
let directionsService;
let directionsRenderer;
let marker;

function initMap() {
  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer();
  const startLat = document.getElementById('start-lat').value;
  const startLng = document.getElementById('start-lng').value;
  const startCoords = new google.maps.LatLng(startLat, startLng);
  const mapOptions = {
    zoom: 8,
    center: startCoords
  };
  map = new google.maps.Map(document.getElementById('map'), mapOptions);
  // Başlangıçta bir marker oluştur
  marker = new google.maps.Marker({
    position: { lat: 39.925018, lng: 32.836956 },
    map: map,
    icon: {
      url: 'car.png', // Araba ikonu URL'si
      scaledSize: new google.maps.Size(64, 64) // Ikon boyutu
    }
  });
  directionsRenderer.setMap(map);
  calculateRoute();
  startTracking('http://localhost:5000/gps');
}

function calculateRoute() {
  const startLat = document.getElementById('start-lat').value;
  const startLng = document.getElementById('start-lng').value;
  const endLat = document.getElementById('end-lat').value;
  const endLng = document.getElementById('end-lng').value;
  const start = new google.maps.LatLng(startLat, startLng);
  const end = new google.maps.LatLng(endLat, endLng);
  const request = {
    origin: start,
    destination: end,
    travelMode: google.maps.TravelMode.DRIVING,
    provideRouteAlternatives: true // Alternatif rotaları almak için
  };
  directionsService.route(request, function(result, status) {
    if (status == google.maps.DirectionsStatus.OK) {
      directionsRenderer.setDirections(result);
      console.log("Alınabilecek toplam rota sayısı: " + result.routes.length);
      document.getElementById('route-count').textContent = `Toplam Rota Sayısı: ${result.routes.length}`;
      showAlternativeRoutes(result); // Alternatif rotaları göstermek için
    } else {
      alert('Rota hesaplanırken bir hata oluştu: ' + status);
    }
  });
}

function calculateEnergyConsumption(route) {
    let distance = 0;
    let elevationGain = 0;
  
    for (let i = 0; i < route.legs.length; i++) {
      distance += route.legs[i].distance.value; // Mesafeyi topla
  
      for (let j = 0; j < route.legs[i].steps.length; j++) {
        const step = route.legs[i].steps[j];
        if (step.elevation) {
          const elevationDiff = step.elevation.endLocation.lng - step.elevation.startLocation.lng;
          if (elevationDiff > 0) {
            elevationGain += elevationDiff; // Yükseltileri topla
          }
        }
      }
    }
  
    // Basit bir enerji tüketimi hesaplama formülü
    const energyConsumption = distance * 0.001 + elevationGain * 0.01; // Uzaklık ve yükseklik değişikliklerinin etkilerini topla
    return energyConsumption;
  }
  
  function getColorForEnergy(energyConsumption) {
    const maxEnergy = 100; // Maksimum enerji tüketimi
    const minEnergy = 0; // Minimum enerji tüketimi
  
    // Enerji tüketimine göre renk belirle
    const hue = ((energyConsumption - minEnergy) / (maxEnergy - minEnergy)) * 120;
    const color = `hsl(${120 - hue}, 100%, 50%)`; // Renk tonunu hesapla
    return color;
  }
  
  function showAlternativeRoutes(result) {
    const routes = result.routes;
    let minEnergy = Infinity;
    let maxEnergy = 0;
  
    // Minimum ve maksimum enerji tüketimlerini bul
    for (let i = 0; i < routes.length; i++) {
      const route = routes[i];
      const energyConsumption = calculateEnergyConsumption(route);
      if (energyConsumption < minEnergy) {
        minEnergy = energyConsumption;
      }
      if (energyConsumption > maxEnergy) {
        maxEnergy = energyConsumption;
      }
    }
  
    const routeList = document.createElement('ul');
    const numRoutesToShow = routes.length < 5 ? routes.length : 5; // Eğer rota sayısı 5'ten azsa tüm rotaları, değilse ilk 5 rotayı göster
    for (let i = 0; i < numRoutesToShow; i++) {
      const route = routes[i];
      const routeItem = document.createElement('li');
      const energyConsumption = calculateEnergyConsumption(route);
  
      let color;
      if (routes.length === 1) {
        color = 'green'; // Tek rota varsa yeşil
      } else if (routes.length === 2) {
        if (energyConsumption === minEnergy) {
          color = 'green'; // En düşük enerji tüketimi yeşil
        } else {
          color = 'red'; // Diğer rota kırmızı
        }
      } else {
        const hue = ((energyConsumption - minEnergy) / (maxEnergy - minEnergy)) * 120;
        color = `hsl(${120 - hue}, 100%, 50%)`; // Renk tonunu hesapla
      }
  
      console.log(`Rota ${i + 1} enerji tüketimi: ${energyConsumption.toFixed(2)} birim`);
  
      const polylineOptions = {
        strokeColor: color,
        strokeWeight: 6,
        zIndex: 1
      };
      const polyline = new google.maps.Polyline(polylineOptions);
      polyline.setPath(route.overview_path);
      polyline.setMap(map);
  
      routeItem.textContent = `Rota ${i + 1}: ${route.summary}`;
      routeItem.textContent = `Rota ${i + 1}: ${route.summary}`;
      routeItem.style.color = color; // Yazı rengini rotanın rengine ayarla
      routeItem.addEventListener('click', function() {
        directionsRenderer.setDirections({ routes: [route] });
      });
      routeList.appendChild(routeItem);
    }
    document.body.appendChild(routeList);
  }

  async function fetchGpsData(endpoint) {
    try {
      const response = await fetch(endpoint);
      const data = await response.json();
      const latitude = parseFloat(data.latitude);
      const longitude = parseFloat(data.longitude);

      // Yeni bir LatLng nesnesi oluştur
      const newPosition = new google.maps.LatLng(latitude, longitude);

      // Marker'ın konumunu güncelle
      marker.setPosition(newPosition);

      // Marker'ı haritaya eklemek için kontrol et
      if (!marker.getMap()) {
        marker.setMap(map);
      }

      // Harita merkezini güncelle
      map.setCenter(newPosition);
      console.log(`Latitude: ${latitude}, Longitude: ${longitude}`);
    } catch (error) {
      console.error('GPS verisi alınırken hata oluştu:', error);
    }
}


  function startTracking(endpoint) {
    fetchGpsData(endpoint); // İlk konumu hemen al
    setInterval(() => fetchGpsData(endpoint), 2000); // Her saniyede bir güncelle
  }  

document.getElementById('calculate-route').addEventListener('click', calculateRoute);

// Google Maps API anahtarınızı buraya ekleyin
// YOUR_API_KEY yerine anahtarınızı yazın
const script = document.createElement('script');
script.src = 'https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap';
document.head.appendChild(script);

