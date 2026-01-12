// Filter functionality
const filterBtn = document.querySelectorAll('.filter-btn');
filterBtn.forEach(btn => {
    btn.addEventListener('click', function() {
        filterBtn.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        console.log('Filter:', this.textContent);
    });
});

// Department card clicks
const deptCards = document.querySelectorAll('.department-card');
deptCards.forEach(card => {
    card.addEventListener('click', function() {
        const filter = this.dataset.filter;
        console.log('Department clicked: ', filter);
    });
});

// Job apply buttons
const applyBtn = document.querySelectorAll('.job-apply');
applyBtn.forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const jobTitle = this.closest('.job-card').querySelector('.job-title').textContent;
        alert(`Applying for: ${jobTitle}`);
    });
});