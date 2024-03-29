$(document).ready(function() {
    // Function to update the dynamic values
    function updateValues() {
      $.ajax({
        url: '/get_values',
        type: 'GET',
        success: function(data) {
          $('#soilMoisture').text(data.soil_moisture);
          $('#ramUsage').text(data.ram_usage);
          $('#cpuUsage').text(data.cpu_usage);
          $('#cpuTemp').text(data.cpu_temp);
          $('#temperature').text(data.temperature_c);
          $('#humidity').text(data.humidity);
        }
      });
    }
  
    // Update values initially
    updateValues();
  
    // Periodically update values every 5 seconds
    setInterval(updateValues, 1000);
  });