// Add active class to current navigation item
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === window.location.pathname) {
            link.classList.add('active');
        }

        link.addEventListener('click', function() {
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

// Ensure forms are visible
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;

    if (currentPath === '/register') {
        const registerForm = document.querySelector('form');
        if (registerForm) {
            console.log('Registration form found');
            registerForm.style.display = 'block';
        } else {
            console.log('Registration form not found');
        }
    } else if (currentPath === '/login') {
        const loginForm = document.querySelector('form');
        if (loginForm) {
            console.log('Login form found');
            loginForm.style.display = 'block';
        } else {
            console.log('Login form not found');
        }
    }
});
