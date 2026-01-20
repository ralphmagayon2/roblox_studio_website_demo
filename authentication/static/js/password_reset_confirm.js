document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const strengthBar = document.getElementById('strengthBar');
    const strengthText = document.getElementById('strengthText');
    const resetForm = document.getElementById('resetForm');
    const resetBtn = document.getElementById('resetBtn');
    
    // Password toggle
    const togglePassword = document.getElementById('togglePassword');
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    
    togglePassword.addEventListener('click', () => {
        const type = passwordInput.type === 'password' ? 'text' : 'password';
        passwordInput.type = type;
        togglePassword.querySelector('i').className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
    });
    
    toggleConfirmPassword.addEventListener('click', () => {
        const type = confirmPasswordInput.type === 'password' ? 'text' : 'password';
        confirmPasswordInput.type = type;
        toggleConfirmPassword.querySelector('i').className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
    });
    
    // Password strength checker
    passwordInput.addEventListener('input', () => {
        const password = passwordInput.value;
        let strength = 0;
        
        // Check requirements
        const hasLength = password.length >= 8;
        const hasUppercase = /[A-Z]/.test(password);
        const hasLowercase = /[a-z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        const hasSpecial = /[^A-Za-z0-9]/.test(password);
        
        // Update requirement indicators
        document.getElementById('req-length').className = hasLength ? 'valid' : '';
        document.getElementById('req-uppercase').className = hasUppercase ? 'valid' : '';
        document.getElementById('req-lowercase').className = hasLowercase ? 'valid' : '';
        document.getElementById('req-number').className = hasNumber ? 'valid' : '';
        document.getElementById('req-special').className = hasSpecial ? 'valid' : '';
        
        // Calculate strength
        if (hasLength) strength++;
        if (hasUppercase) strength++;
        if (hasLowercase) strength++;
        if (hasNumber) strength++;
        if (hasSpecial) strength++;
        
        // Update strength bar
        strengthBar.className = 'password-strength-bar';
        if (strength <= 2) {
            strengthBar.classList.add('weak');
            strengthText.textContent = 'Weak password';
            strengthText.style.color = '#ff4757';
        } else if (strength <= 4) {
            strengthBar.classList.add('medium');
            strengthText.textContent = 'Medium password';
            strengthText.style.color = '#ffa502';
        } else {
            strengthBar.classList.add('strong');
            strengthText.textContent = 'Strong password';
            strengthText.style.color = '#2ed573';
        }
    });
    
    // Form submission
    resetForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (password !== confirmPassword) {
            alert('Passwords do not match!');
            return;
        }
        
        if (password.length < 8) {
            alert('Password must be at least 8 characters!');
            return;
        }
        
        resetBtn.disabled = true;
        resetBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Resetting...';
        resetForm.submit();
    });
});