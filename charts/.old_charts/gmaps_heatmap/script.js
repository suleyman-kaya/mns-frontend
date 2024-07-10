// script.js

document.addEventListener('DOMContentLoaded', function() {
    const mapContainer = document.getElementById('map');
    const visualizeButton = document.getElementById('visualizeButton');

    visualizeButton.addEventListener('click', visualizeData);

    function visualizeData() {
        const apiKey = getUrlParameter('api');
        if (!apiKey) {
            alert('API anahtarı belirtilmedi.');
            return;
        }

        const fileInput = document.getElementById('csvFileInput');
        const file = fileInput.files[0];
        Papa.parse(file, {
            header: true,
            dynamicTyping: true,
            complete: function(results) {
                const data = results.data;
                const heatmapData = data.map(item => ({
                    location: new google.maps.LatLng(item.lat, item.long),
                    weight: item.joule
                }));

                const map = new google.maps.Map(mapContainer, {
                    zoom: 11,
                    center: { lat: 39.9334, lng: 32.8597 }
                });

                const heatmap = new google.maps.visualization.HeatmapLayer({
                    data: heatmapData,
                    map: map
                });
            }
        });
    }

    function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        const results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }
});
