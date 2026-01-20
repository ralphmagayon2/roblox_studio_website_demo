// ============================================
// ROBLOX AUTHENTICATION - Complete System
// Global scripts + Page-specific functionality
// ============================================

document.addEventListener("DOMContentLoaded", () => {
    
    // ========================================
    // GLOBAL FEATURES (Run on ALL pages)
    // ========================================
    
    // Background Square Generation
    function createBackgroundSquares() {
        const container = document.getElementById('bgContainer');
        if (!container) return; // Exit if container doesn't exist
        
        const numberOfSquares = 15;
        const sizes = ['small', 'medium', 'large'];
        const positions = [
            // Top left
            { x: 5, y: 5 },
            { x: 15, y: 10 },
            { x: 10, y: 20 },
            // Top right
            { x: 85, y: 8 },
            { x: 90, y: 15 },
            { x: 80, y: 5 },
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
    
    // Mobile Menu Toggle
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navLinks = document.getElementById('navLinks');
    
    if (mobileMenuToggle && navLinks) {
        mobileMenuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            const icon = mobileMenuToggle.querySelector('i');
            if (icon) {
                icon.className = navLinks.classList.contains('active') ? 'fa-solid fa-times' : 'fa-solid fa-bars';
            }
        });
    }
    
    // Initialize background (runs on all pages)
    createBackgroundSquares();
    
    
    // ========================================
    // LOGIN/SIGNUP PAGE ONLY
    // ========================================
    
    // Check if we're on the login/signup page
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    
    if (loginForm || signupForm) {
        // We're on the auth page, run auth-specific code
        initAuthPage();
    }
});


// ========================================
// AUTH PAGE INITIALIZATION
// ========================================

function initAuthPage() {
    
    // ========================================
    // TAB SWITCHING
    // ========================================
    
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
            
            // Show corresponding form and update header
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
    
    
    // ========================================
    // FORM ELEMENTS
    // ========================================
    
    // Login Form
    const loginForm = document.getElementById('loginForm');
    const loginUsername = document.getElementById('login_username');
    const loginPassword = document.getElementById('login_password');
    
    // Signup Form
    const signupForm = document.getElementById('signupForm');
    const signupUsername = document.getElementById('signup_username');
    const signupEmail = document.getElementById('signup_email');
    const signupPassword = document.getElementById('signup_password');
    const signupConfirmPassword = document.getElementById('signup_confirm_password');
    const agreeTerms = document.getElementById('agreeTerms');
    
    // Social Buttons
    const googleButtons = document.querySelectorAll('.btn-social.google');
    const discordButtons = document.querySelectorAll('.btn-social.discord');
    
    
    // ========================================
    // AUTO-HIDE DJANGO MESSAGES
    // ========================================
    
    const autoHideDjangoMessages = () => {
        const messages = document.querySelectorAll('.message, .invalid-message');
        messages.forEach(message => {
            setTimeout(() => {
                message.style.animation = 'slideUp 0.4s ease-out forwards';
                setTimeout(() => message.remove(), 400);
            }, 5000);
        });
    };
    
    autoHideDjangoMessages();
    
    
    // ========================================
    // HELPER FUNCTIONS
    // ========================================
    
    const setError = (input, message) => {
        // Find the form-group (might need to go up 2 levels if input is in password-input-wrapper)
        let formGroup = input.parentElement;

        // If parent is password-input-wrapper, go up one more level
        if (formGroup.classList.contains('password-input-wrapper')) {
            formGroup = formGroup.parentElement;
        }

        const errorDisplay = formGroup.querySelector('.error');

        if (errorDisplay) {
            errorDisplay.innerText = message;
        }

        formGroup.classList.add('error');
        formGroup.classList.remove('success');
    };

    const setSuccess = (input) => {
        // Find the form-group (might need to go up 2 levels if input is in password-input-wrapper)
        let formGroup = input.parentElement;

        // If parent is password-input-wrapper, go up one more level
        if (formGroup.classList.contains('password-input-wrapper')) {
            formGroup = formGroup.parentElement;
        }

        const errorDisplay = formGroup.querySelector('.error');

        if (errorDisplay) {
            errorDisplay.innerText = '';
        }

        formGroup.classList.add('success');
        formGroup.classList.remove('error');
    };
    
    const clearServerMessages = () => {
        const serverMessages = document.querySelectorAll('.message, .invalid-message');
        serverMessages.forEach(message => {
            message.style.animation = 'slideUp 0.3s ease-out forwards';
            setTimeout(() => message.remove(), 300);
        });
    };
    
    const isValidEmail = (email) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    };
    
    const isValidUsername = (username) => {
        // 3-20 characters, letters, numbers, underscores only
        const regex = /^[a-zA-Z0-9_]{3,20}$/;
        return regex.test(username);
    };
    
    const getPasswordStrength = (password) => {
        let strength = 0;
        
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;
        
        if (strength <= 2) return 'weak';
        if (strength <= 3) return 'medium';
        return 'strong';
    };
    
    
    // ========================================
    // LOGIN FORM VALIDATION
    // ========================================
    
    const validateLoginUsername = () => {
        if (!loginUsername) return true; // Skip if element doesn't exist
        
        const value = loginUsername.value.trim();
        
        if (!value) {
            setError(loginUsername, 'Username or email is required');
            return false;
        }
        
        // If it contains @, validate as email
        if (value.includes('@')) {
            if (!isValidEmail(value)) {
                setError(loginUsername, 'Please enter a valid email address');
                return false;
            }
        }
        
        setSuccess(loginUsername);
        return true;
    };
    
    const validateLoginPassword = () => {
        if (!loginPassword) return true; // Skip if element doesn't exist
        
        const value = loginPassword.value.trim();
        
        if (!value) {
            setError(loginPassword, 'Password is required');
            return false;
        }
        
        setSuccess(loginPassword);
        return true;
    };
    
    // Login Form Event Listeners
    if (loginForm) {
        if (loginUsername) {
            loginUsername.addEventListener('blur', validateLoginUsername);
            loginUsername.addEventListener('input', () => {
                validateLoginUsername();
                clearServerMessages();
            });
        }
        
        if (loginPassword) {
            loginPassword.addEventListener('blur', validateLoginPassword);
            loginPassword.addEventListener('input', () => {
                validateLoginPassword();
                clearServerMessages();
            });
        }
        
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const isUsernameValid = validateLoginUsername();
            const isPasswordValid = validateLoginPassword();
            
            if (isUsernameValid && isPasswordValid) {
                const submitBtn = loginForm.querySelector('button[type="submit"]');
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing In...';
                
                // Submit the form
                loginForm.submit();
            }
        });
    }
    
    
    // ========================================
    // SIGNUP FORM VALIDATION
    // ========================================
    
    const validateSignupUsername = () => {
        if (!signupUsername) return true;
        
        const value = signupUsername.value.trim();
        
        if (!value) {
            setError(signupUsername, 'Username is required');
            return false;
        }
        
        if (value.length < 3) {
            setError(signupUsername, 'Username must be at least 3 characters');
            return false;
        }
        
        if (value.length > 20) {
            setError(signupUsername, 'Username must be less than 20 characters');
            return false;
        }
        
        if (!isValidUsername(value)) {
            setError(signupUsername, 'Username can only contain letters, numbers, and underscores');
            return false;
        }
        
        setSuccess(signupUsername);
        return true;
    };
    
    const validateSignupEmail = () => {
        if (!signupEmail) return true;
        
        const value = signupEmail.value.trim();
        
        if (!value) {
            setError(signupEmail, 'Email is required');
            return false;
        }
        
        if (!isValidEmail(value)) {
            setError(signupEmail, 'Please enter a valid email address');
            return false;
        }
        
        setSuccess(signupEmail);
        return true;
    };
    
    const validateSignupPassword = () => {
        if (!signupPassword) return true;
        
        const value = signupPassword.value.trim();
        
        if (!value) {
            setError(signupPassword, 'Password is required');
            return false;
        }
        
        if (value.length < 8) {
            setError(signupPassword, 'Password must be at least 8 characters');
            return false;
        }
        
        // Check password strength
        const strength = getPasswordStrength(value);
        if (strength === 'weak') {
            setError(signupPassword, 'Password is too weak. Add uppercase, numbers, or symbols');
            return false;
        }
        
        setSuccess(signupPassword);
        
        // Re-validate confirm password if it has a value
        if (signupConfirmPassword && signupConfirmPassword.value) {
            validateSignupConfirmPassword();
        }
        
        return true;
    };
    
    const validateSignupConfirmPassword = () => {
        if (!signupConfirmPassword || !signupPassword) return true;
        
        const password = signupPassword.value.trim();
        const confirmPassword = signupConfirmPassword.value.trim();
        
        if (!confirmPassword) {
            setError(signupConfirmPassword, 'Please confirm your password');
            return false;
        }
        
        if (password !== confirmPassword) {
            setError(signupConfirmPassword, 'Passwords do not match');
            return false;
        }
        
        setSuccess(signupConfirmPassword);
        return true;
    };
    
    const validateTerms = () => {
        if (!agreeTerms) return true;
        
        if (!agreeTerms.checked) {
            alert('You must agree to the Terms of Service');
            return false;
        }
        return true;
    };
    
    // Signup Form Event Listeners
    if (signupForm) {
        if (signupUsername) {
            signupUsername.addEventListener('blur', validateSignupUsername);
            signupUsername.addEventListener('input', () => {
                validateSignupUsername();
                clearServerMessages();
            });
        }
        
        if (signupEmail) {
            signupEmail.addEventListener('blur', validateSignupEmail);
            signupEmail.addEventListener('input', () => {
                validateSignupEmail();
                clearServerMessages();
            });
        }
        
        if (signupPassword) {
            signupPassword.addEventListener('blur', validateSignupPassword);
            signupPassword.addEventListener('input', () => {
                validateSignupPassword();
                clearServerMessages();
            });
        }
        
        if (signupConfirmPassword) {
            signupConfirmPassword.addEventListener('blur', validateSignupConfirmPassword);
            signupConfirmPassword.addEventListener('input', () => {
                validateSignupConfirmPassword();
                clearServerMessages();
            });
        }
        
        signupForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const isUsernameValid = validateSignupUsername();
            const isEmailValid = validateSignupEmail();
            const isPasswordValid = validateSignupPassword();
            const isConfirmPasswordValid = validateSignupConfirmPassword();
            const isTermsValid = validateTerms();
            
            if (isUsernameValid && isEmailValid && isPasswordValid && isConfirmPasswordValid && isTermsValid) {
                const submitBtn = signupForm.querySelector('button[type="submit"]');
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...';
                
                // Submit the form
                signupForm.submit();
            }
        });
    }
    
    
    // ========================================
    // OAUTH HANDLERS (Google & Discord)
    // ========================================
    
    // Google OAuth
    googleButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Show loading state
            button.disabled = true;
            const originalContent = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';
            
            // Redirect to Google OAuth endpoint
            // TODO: Set up django-allauth and configure Google OAuth
            window.location.href = '/accounts/google/login/';
            
            // Fallback if redirect fails
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = originalContent;
            }, 3000);
        });
    });
    
    // Discord OAuth
    discordButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Show loading state
            button.disabled = true;
            const originalContent = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';
            
            // Redirect to Discord OAuth endpoint
            // TODO: Set up django-allauth and configure Discord OAuth
            window.location.href = '/accounts/discord/login/';
            
            // Fallback if redirect fails
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = originalContent;
            }, 3000);
        });
    });

    // ========================================
    // PASSWORD VISIBILITY TOGGLE
    // ========================================

    const togglePasswordVisibility = (inputId, toggleBtnId) => {
        const input = document.getElementById(inputId);
        const toggleBtn = document.getElementById(toggleBtnId);
        
        if (input && toggleBtn) {
            toggleBtn.addEventListener('click', (e) => {
                e.preventDefault(); // Prevent form submission
                
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);
                
                // Toggle icon
                const icon = toggleBtn.querySelector('i');
                if (icon) {
                    if (type === 'password') {
                        icon.classList.remove('fa-eye-slash');
                        icon.classList.add('fa-eye');
                    } else {
                        icon.classList.remove('fa-eye');
                        icon.classList.add('fa-eye-slash');
                    }
                }
            });
        }
    };

    // Initialize password toggles
    togglePasswordVisibility('login_password', 'toggleLoginPassword');
    togglePasswordVisibility('signup_password', 'toggleSignupPassword');
    togglePasswordVisibility('signup_confirm_password', 'toggleConfirmPassword');
}


// ========================================
// SLIDE UP ANIMATION (for messages)
// ========================================

const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        0% {
            opacity: 1;
            transform: translateY(0);
        }
        100% {
            opacity: 0;
            transform: translateY(-10px);
        }
    }
`;
document.head.appendChild(style);