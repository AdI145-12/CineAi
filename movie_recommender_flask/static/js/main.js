// ── Theme ──────────────────────────────────────────────────
(function(){
  const d = window.matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', d);
})();

// ── Autocomplete Search ────────────────────────────────────
const input = document.getElementById('search-input');
const dropdown = document.getElementById('autocomplete');

if (input && dropdown) {
  let debounce;
  input.addEventListener('input', () => {
    clearTimeout(debounce);
    const q = input.value.trim();
    if (q.length < 2) { dropdown.classList.remove('open'); return; }
    debounce = setTimeout(async () => {
      try {
        const res = await fetch(`/api/movies?q=${encodeURIComponent(q)}`);
        const movies = await res.json();
        dropdown.innerHTML = '';
        if (movies.length === 0) { dropdown.classList.remove('open'); return; }
        movies.forEach(title => {
          const div = document.createElement('div');
          div.className = 'autocomplete-item';
          div.textContent = title;
          div.addEventListener('click', () => {
            window.location.href = `/recommend/${encodeURIComponent(title)}`;
          });
          dropdown.appendChild(div);
        });
        dropdown.classList.add('open');
      } catch(e) { dropdown.classList.remove('open'); }
    }, 250);
  });

  document.addEventListener('click', (e) => {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.remove('open');
    }
  });
}

// ── Tab Switching ──────────────────────────────────────────
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    const target = document.getElementById('tab-' + tab.dataset.tab);
    if (target) target.classList.add('active');
  });
});

// ── Flash auto-dismiss ─────────────────────────────────────
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(f => {
    f.style.transition = 'opacity 0.5s';
    f.style.opacity = '0';
    setTimeout(() => f.remove(), 500);
  });
}, 3000);
