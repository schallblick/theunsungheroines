// ── Data loading ──────────────────────────────────────────────────────────
fetch('unsung_heroines_data.json')
    .then(r => r.json())
    .then(data => {
        const container = document.getElementById('heroine-content');
        const weekNumber = Math.floor(Date.now() / (7 * 24 * 60 * 60 * 1000));
        const heroine = data[weekNumber % data.length];

        if (!heroine || !heroine.name) {
            container.innerHTML = '<p class="state-message">No featured heroine this week.</p>';
            return;
        }

        container.innerHTML = buildCard(heroine);
    })
    .catch(() => {
        document.getElementById('heroine-content').innerHTML =
            '<p class="state-message">Could not load data. Please try again later.</p>';
    });

// ── Card builder ──────────────────────────────────────────────────────────
function buildCard(h) {
    return `
      <div class="heroine-card">
        ${buildPortrait(h)}
        <div class="heroine-body">
          ${buildHeader(h)}
          ${buildChips(h)}
          ${buildBiography(h)}
          ${buildSources(h)}
        </div>
      </div>`;
}

function buildPortrait(h) {
    if (h.image) {
        const credit = h.image_credit || '';
        return `
          <div class="heroine-portrait">
            <img src="${h.image}" alt="Portrait of ${h.name}" loading="lazy">
            ${credit ? `<p class="image-credit">${credit}</p>` : ''}
          </div>`;
    }
    // No image — show initials placeholder
    const initials = h.name
        .split(' ')
        .filter(Boolean)
        .slice(0, 2)
        .map(w => w[0].toUpperCase())
        .join('');
    return `
      <div class="heroine-portrait no-image">
        <div class="heroine-initials" aria-hidden="true">${initials}</div>
      </div>`;
}

function buildHeader(h) {
    const dates = (h.birth_date || h.death_date)
        ? `<p class="heroine-dates">${h.birth_date || '?'} – ${h.death_date || 'present'}</p>`
        : '';
    return `
      <div>
        <p class="heroine-label">Featured Heroine</p>
        <h2 class="heroine-name">${h.name}</h2>
        ${dates}
      </div>`;
}

function buildChips(h) {
    if (!h.fields || !h.fields.length) return '';
    const chips = h.fields
        .map(f => `<span class="chip">${f}</span>`)
        .join('');
    return `<div class="field-chips">${chips}</div>`;
}

function buildBiography(h) {
    const raw = h.biography || h.extract || h.description || 'No biography available.';
    // Convert newlines to paragraphs for clean HTML rendering
    const paras = raw
        .split(/\n{2,}/)
        .map(p => p.replace(/\n/g, ' ').trim())
        .filter(Boolean)
        .map(p => `<p>${p}</p>`)
        .join('');
    return `<div class="biography">${paras || `<p>${raw}</p>`}</div>`;
}

function buildSources(h) {
    if (!h.sources || !h.sources.length) return '';
    const items = h.sources
        .map(s => `<li><a href="${s.url}" target="_blank" rel="noopener noreferrer">${s.name}</a></li>`)
        .join('');
    return `
      <div class="sources">
        <hr class="heroine-divider">
        <p class="sources-label">Sources</p>
        <ul class="sources-list">${items}</ul>
      </div>`;
}

// ── Accessibility toggles ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;

    // Restore saved preferences
    if (localStorage.getItem('theme') === 'dark')     body.classList.add('dark-theme');
    if (localStorage.getItem('font')  === 'dyslexic') body.classList.add('dyslexic-font');

    document.getElementById('theme-toggle').addEventListener('click', () => {
        body.classList.toggle('dark-theme');
        localStorage.setItem('theme', body.classList.contains('dark-theme') ? 'dark' : 'light');
    });

    document.getElementById('font-toggle').addEventListener('click', () => {
        body.classList.toggle('dyslexic-font');
        localStorage.setItem('font', body.classList.contains('dyslexic-font') ? 'dyslexic' : 'default');
    });
});
