document.getElementById('login').addEventListener('submit', function(e) {


    document.querySelectorAll('.error').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.form-control').forEach(el => el.classList.remove('error-input'));

    let isValid = true;
    const username = document.getElementById('username');
    const password = document.getElementById('password');

    if (!username.value.trim()) {
        document.getElementById('errorUsername').style.display = 'block';
        username.classList.add('error-input');
        isValid = false;
    }

    if (!password.value.trim()) {
        document.getElementById('errorPassword').style.display = 'block';
        password.classList.add('error-input');
        isValid = false;
    }

    if (isValid) {
        fetch('/admin/login', {
            method: 'POST',
            body: new FormData(this)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/admin/dashboard';
            } else {
                alert(data.error || 'Error al iniciar sesión. Por favor, inténtalo de nuevo.');
            }
        })
        .catch(error => {
            console.error('Error al enviar el formulario:', error);
            alert('Error al iniciar sesión. Por favor, inténtalo de nuevo más tarde.');
        });
    }



})