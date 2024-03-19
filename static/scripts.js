$(document).ready(function() {
    function updateSystemInfo() {
        $.ajax({
            url: '/', // Replace with the endpoint to fetch the system information
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                // Update RAM usage
                $('#ram-usage').text(data.ram_usage + '%');
                
                // Update CPU usage
                $('#cpu-usage').text(data.cpu_usage + '%');
                
                // Update CPU temperature
                if (data.cpu_temp !== 'N/A') {
                    $('#cpu-temp').text(data.cpu_temp.current + ' Celcius');
                } else {
                    $('#cpu-temp').text('N/A');
                }
            }
        });
    }
    
    // Update system info initially and then every 5 seconds
    updateSystemInfo();
    setInterval(updateSystemInfo, 5000);
});