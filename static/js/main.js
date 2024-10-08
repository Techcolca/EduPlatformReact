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

// Ensure form is visible
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (form) {
        console.log('Registration form found');
        form.style.display = 'block';
    } else {
        console.log('Registration form not found');
    }
});
