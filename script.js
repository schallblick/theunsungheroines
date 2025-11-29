fetch('unsung_heroines_data.json')
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById('heroine-content');
        const today = new Date();
        const weekNumber = Math.floor(today.getTime() / (7 * 24 * 60 * 60 * 1000)); // Calculate week number

        const featuredHeroine = data[weekNumber % data.length]; // Select heroine based on week number

        if (featuredHeroine && featuredHeroine.title && featuredHeroine.extract) {
            let imageHtml = '';
            if (featuredHeroine.image) {
                imageHtml = `<img src="${featuredHeroine.image}" alt="${featuredHeroine.title}">`;
            }

            container.innerHTML = `
                ${imageHtml}
                <div>
                    <h2>${featuredHeroine.title}</h2>
                    <p>${featuredHeroine.extract}</p>
                    <a href="${featuredHeroine.full_url}" target="_blank" aria-label="Read more about ${featuredHeroine.title} on Wikipedia">Read more on Wikipedia</a>
                </div>
            `;
        } else {
            container.innerHTML = '<p>No featured heroine this week.</p>';
        }
    })
    .catch(error => console.error('Error loading data:', error));

// Theme and Font Toggles
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const fontToggle = document.getElementById('font-toggle');
    const body = document.body;

    // Load saved preferences
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-theme');
    }
    if (localStorage.getItem('font') === 'dyslexic') {
        body.classList.add('dyslexic-font');
    }

    // Theme Toggle Listener
    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-theme');
        if (body.classList.contains('dark-theme')) {
            localStorage.setItem('theme', 'dark');
        } else {
            localStorage.setItem('theme', 'light');
        }
    });

    // Font Toggle Listener
    fontToggle.addEventListener('click', () => {
        body.classList.toggle('dyslexic-font');
        if (body.classList.contains('dyslexic-font')) {
            localStorage.setItem('font', 'dyslexic');
        } else {
            localStorage.setItem('font', 'default');
        }
    });
});