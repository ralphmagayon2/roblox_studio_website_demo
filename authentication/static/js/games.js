// Filter buttons functionality
const filterButtons = document.querySelectorAll('.filter-btn');
filterButtons.forEach(button => {
    button.addEventListener('click', () => {
        filterButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        console.log('Filter:', button.textContent);
        // Add actual filtering logic here
    });
});

// Search functionality
const searchInput = document.querySelector('.search-input');
searchInput.addEventListener('input', (e) => {
    console.log('Search:', e.target.value);
    // Add actual search logic here
});

// Play button clicks
const playButtons = document.querySelectorAll('.play-btn');
playButtons.forEach(button => {
    button.addEventListener('click', (e) => {
        e.stopPropagation();
        const gameCard = button.closest('.game-card');
        const gameTitle = gameCard.querySelector('.game-title').textContent;
        alert(`Launching ${gameTitle}...`);
        // Add actual game launch logic here
    });
});

// Game card clicks
const gameCards = document.querySelectorAll('.game-card');
gameCards.forEach(card => {
    card.addEventListener('click', () => {
        const gameTitle = card.querySelector('.game-title').textContent;
        console.log('Game clicked:', gameTitle);
        // Navigate to game details page
    });
});

// Load more button
const loadMoreBtn = document.querySelector('.btn-load-more');
loadMoreBtn.addEventListener('click', () => {
    alert('Loading more games...');
    // Add pagination logic here
});