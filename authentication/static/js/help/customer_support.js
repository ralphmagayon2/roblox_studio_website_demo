// Smooth scroll to form when clicking "Create Ticket"
document.querySelectorAll('a[href="#submit-ticket"]').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        document.getElementById('submit-ticket').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    });
});