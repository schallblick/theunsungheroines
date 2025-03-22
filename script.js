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
                    <a href="${featuredHeroine.full_url}" target="_blank">Read more on Wikipedia</a>
                </div>
            `;
        } else {
            container.innerHTML = '<p>No featured heroine this week.</p>';
        }
    })
    .catch(error => console.error('Error loading data:', error));