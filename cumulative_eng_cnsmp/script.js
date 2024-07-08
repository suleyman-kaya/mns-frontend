let chart;

document.getElementById('csvFile').addEventListener('change', uploadCSV);

function uploadCSV(event) {
  const file = event.target.files[0];
  Papa.parse(file, {
    complete: function(results) {
      processData(results.data);
    }
  });
}

function processData(data) {
  const lapData = data.slice(1).map(row => ({
    lapNumber: parseInt(row[0]),
    time: parseFloat(row[1]),
    distance: parseFloat(row[2]),
    avgSpeed: parseFloat(row[3]),
    maxSpeed: parseFloat(row[4]),
    joulesUsed: parseInt(row[5])
  })).filter(row => !isNaN(row.joulesUsed));

  updateChart(lapData);
  updateTable(lapData);
}

function updateChart(data) {
  const ctx = document.getElementById('energyChart').getContext('2d');
  
  if (chart) {
    chart.destroy();
  }

  const maxEnergy = Math.max(...data.map(d => d.joulesUsed));
  const minEnergy = Math.min(...data.map(d => d.joulesUsed));

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(d => d.distance),
      datasets: [{
        label: 'Cumulative Electrical Energy Consumption',
        data: data.map(d => d.joulesUsed),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      scales: {
        x: {
          title: {
            display: true,
            text: 'Lap Distance [m]'
          }
        },
        y: {
          title: {
            display: true,
            text: 'Cumulative Energy Consumption [Joules]'
          },
          min: minEnergy,
          max: maxEnergy,
          suggestedMin: minEnergy,
          suggestedMax: maxEnergy
        }
      }
    }
  });
}

function updateTable(data) {
  const tableBody = document.querySelector('#lapTable tbody');
  tableBody.innerHTML = '';

  data.forEach(lap => {
    const row = tableBody.insertRow();
    row.insertCell(0).textContent = lap.lapNumber;
    row.insertCell(1).textContent = lap.time.toFixed(1);
    row.insertCell(2).textContent = lap.distance.toFixed(1);
    row.insertCell(3).textContent = lap.avgSpeed.toFixed(1);
    row.insertCell(4).textContent = lap.maxSpeed.toFixed(1);
    row.insertCell(5).textContent = lap.joulesUsed;
  });
}