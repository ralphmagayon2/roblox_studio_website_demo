document.addEventListener('DOMContentLoaded', () => {
    const resetForm = document.getElementById('resetForm');
    const resetBtn = document.getElementById('resetBtn');

    resetForm.addEventListener('submit', (e) => {
        resetBtn.disabled = true;
        resetBtn.innerHTML = '<i class=""fas fa-spinner fa-spin></i> Sending...';
    });
});