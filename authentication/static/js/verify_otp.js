document.addEventListener('DOMContentLoaded', () => {
    const digits = document.querySelectorAll('.otp-digit');
    const otpValue = document.getElementById('otpValue');
    const otpForm = document.getElementById('otpForm');
    const verifyBtn = document.getElementById('verifyBtn');
    const resendBtn = document.getElementById('resendBtn');
    const timerDisplay = document.getElementById('timer');
    
    // Auto-focus and navigation
    digits.forEach((digit, index) => {
        // Handle input
        digit.addEventListener('input', (e) => {
            const value = e.target.value;
            
            // Only allow single digit
            if (value.length > 1) {
                e.target.value = value.slice(0, 1);
            }
            
            // Move to next digit
            if (value && index < digits.length - 1) {
                digits[index + 1].focus();
            }
            
            // Update hidden input
            updateOTPValue();
        });
        
        // Handle backspace
        digit.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && !e.target.value && index > 0) {
                digits[index - 1].focus();
            }
        });
        
        // Prevent non-numeric input
        digit.addEventListener('keypress', (e) => {
            if (!/[0-9]/.test(e.key)) {
                e.preventDefault();
            }
        });
        
        // Handle paste
        digit.addEventListener('paste', (e) => {
            e.preventDefault();
            const pastedData = e.clipboardData.getData('text').replace(/\D/g, '');
            
            if (pastedData.length === 6) {
                pastedData.split('').forEach((char, i) => {
                    if (digits[i]) {
                        digits[i].value = char;
                    }
                });
                digits[5].focus();
                updateOTPValue();
            }
        });
    });
    
    // Update hidden OTP value
    function updateOTPValue() {
        const otp = Array.from(digits).map(d => d.value).join('');
        otpValue.value = otp;
        
        // Enable/disable verify button
        verifyBtn.disabled = otp.length !== 6;
    }
    
    // Form submission
    otpForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const otp = otpValue.value;
        if (otp.length === 6) {
            verifyBtn.disabled = true;
            verifyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';
            otpForm.submit();
        }
    });
    
    // Resend timer
    let timeLeft = 60;
    let timerInterval;
    
    function startTimer() {
        resendBtn.disabled = true;
        timerInterval = setInterval(() => {
            timeLeft--;
            timerDisplay.textContent = `(${timeLeft}s)`;
            
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                resendBtn.disabled = false;
                timerDisplay.textContent = '';
                timeLeft = 60;
            }
        }, 1000);
    }
    
    // Start timer on page load
    startTimer();
    
    // Handle resend
    document.getElementById('resendForm').addEventListener('submit', (e) => {
        e.preventDefault();
        
        resendBtn.disabled = true;
        resendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        
        fetch("{% url 'authentication:resend_otp' %}", {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (response.ok) {
                resendBtn.innerHTML = '<i class="fas fa-check"></i> Code Sent!';
                setTimeout(() => {
                    resendBtn.innerHTML = '<i class="fas fa-envelope"></i> Resend Code';
                    startTimer();
                }, 2000);
            } else {
                resendBtn.innerHTML = '<i class="fas fa-times"></i> Failed';
                resendBtn.disabled = false;
            }
        });
    });
});