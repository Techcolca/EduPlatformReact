// Simple frontend routing
const routes = {
    '/': home,
    '/about': about
};

function home() {
    document.querySelector('main').innerHTML = '<h1>Welcome to our Educational Platform</h1><p>Start learning today!</p>';
}

function about() {
    document.querySelector('main').innerHTML = '<h1>About Us</h1><p>We are dedicated to providing quality education.</p>';
}

function router() {
    let url = location.hash.slice(1) || '/';
    let route = routes[url];

    if (route) {
        route();
    }
}

window.addEventListener('hashchange', router);
window.addEventListener('load', router);

// Add active class to current navigation item
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === location.hash) {
            link.classList.add('active');
        }

        link.addEventListener('click', function() {
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

// Comment out any code that might affect form visibility
// No such code found in this file
