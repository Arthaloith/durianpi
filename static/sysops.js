function sendPostRequest(event, url) {
    event.preventDefault(); // Prevent the default link behavior

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = url;

    document.body.appendChild(form);
    form.submit();
}