// Background Square Generation
function createBackgroundSquares() {
    const container = document.getElementById('bgContainer');
    const numberOfSquares = 15;
    const sizes = ['small', 'medium', 'large'];
    const positions = [
        // Top left
        { x: 5, y: 5 },
        { x: 15 , y: 10 },
        { x: 10, y: 20 },
        // Top right
        { x: 85, y: 8 },
        { x: 90, y: 15 },
        { x: 80, y: 5},
        // Bottom left
        { x: 8, y: 85 },
        { x: 12, y: 90 },
        { x: 5, y: 78 },
        // Bottom right
        { x: 88, y: 82 },
        { x: 85, y: 90 },
        { x: 92, y: 88 },
        // Centralized
        { x: 45, y: 25 },
        { x: 55, y: 70 },
        { x: 30, y: 50 }
    ];

    for (let i = 0; i < numberOfSquares; i++) {
        const square = document.createElement('div');
        square.className = `bg-square ${sizes[Math.floor(Math.random() * sizes.length)]}`;
        const pos = positions[i];
        square.style.left = `${pos.x}%`;
        square.style.top = `${pos.y}%`;
        square.style.animationDelay = `${Math.random() * 6}s, ${Math.random() * 5}s`;
        const randomRotation = Math.random() * 45;
        square.style.transform = `rotate(${randomRotation}deg)`;
        container.appendChild(square);
    }
}

// Tab Switching
const tabButtons = document.querySelectorAll('.tab-btn');
const forms = document.querySelectorAll('.auth-form');

tabButtons.forEach(button => {
    button.addEventListener('click', () => {

        const targetTab = button.dataset.tab;

        // Remove active class from all buttons and forms
        tabButtons.forEach(btn => btn.classList.remove('active'));
        forms.forEach(form => form.classList.remove('active'));

        // Add active class to clicked button
        button.classList.add('active');

        // Show corresponding form
        if (targetTab === 'login') {
            document.getElementById('loginForm').classList.add('active');
            document.querySelector('.auth-title').textContent = 'Welcome Back';
            document.querySelector('.auth-subtitle').textContent = 'Sign in to continue your adventure';
        } else {
            document.getElementById('signupForm').classList.add('active');
            document.querySelector('.auth-title').textContent = 'Join Roblox';
            document.querySelector('.auth-subtitle').textContent = 'Create an account to start building';
        }
    });
});

// Mobile Menu Toggle
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const navLinks = document.getElementById('navLinks');

mobileMenuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('active');
    mobileMenuToggle.textContent = navLinks.classList.contains('active') ? '✕' : '☰';
});

// Form submission handles
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Login functionality would be implemented here!');
    });
}

const signupForm = document.getElementById('signupForm');
if (signupForm) {
    signupForm.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Sign up functionality would be implemented here!');
    });
}

// This will now run even if the forms are missing
createBackgroundSquares();