function sendPostRequest(event, url) {
    event.preventDefault(); // Prevent the default link behavior
  
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => {
      if (response.ok) {
        // Redirect the user to the login page or any other desired location
        window.location.href = '/login';
      } else {
        console.error('Error:', response.status);
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }