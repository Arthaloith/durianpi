function sendPostRequest(event, url) {
    event.preventDefault(); 

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = url;

    document.body.appendChild(form);
    form.submit();
}