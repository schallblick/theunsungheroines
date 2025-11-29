fetch('unsung_heroines_data.json')
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById('heroine-content');
        const today = new Date();
        const weekNumber = Math.floor(today.getTime() / (7 * 24 * 60 * 60 * 1000));

        const featuredHeroine = data[weekNumber % data.length];

        if (featuredHeroine && featuredHeroine.name) {
            let imageHtml = '';
            if (featuredHeroine.image) {
                const imageCredit = featuredHeroine.image_credit || 'Image source: ' + (featuredHeroine.sources?.[0]?.name || 'Unknown');
                imageHtml = `
                    <div class="heroine-image">
                        <img src="${featuredHeroine.image}" alt="${featuredHeroine.name}">
                        <p class="image-credit">${imageCredit}</p>
                    </div>
                `;
            }

            // Build sources HTML
            let sourcesHtml = '';
            if (featuredHeroine.sources && featuredHeroine.sources.length > 0) {
                sourcesHtml = '<div class="sources"><h3>Sources</h3><ul>';
                featuredHeroine.sources.forEach(source => {
                    sourcesHtml += `<li><a href="${source.url}" target="_blank" rel="noopener noreferrer">${source.name}</a> (accessed ${source.accessed})</li>`;
                });
                sourcesHtml += '</ul></div>';
            }

            // Get biography from various possible fields
            const biography = featuredHeroine.biography || featuredHeroine.extract || featuredHeroine.description || 'No biography available.';

            container.innerHTML = `
                ${imageHtml}
                <div class="heroine-info">
                    <h2>${featuredHeroine.name}</h2>
                    ${featuredHeroine.birth_date || featuredHeroine.death_date ?
                    `<p class="dates">${featuredHeroine.birth_date || '?'} - ${featuredHeroine.death_date || 'present'}</p>` : ''}
                    ${featuredHeroine.fields && featuredHeroine.fields.length > 0 ?
                    `<p class="fields"><strong>Fields:</strong> ${featuredHeroine.fields.join(', ')}</p>` : ''}
                    <p class="biography">${biography}</p>
                    ${sourcesHtml}
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