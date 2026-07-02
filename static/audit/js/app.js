document.addEventListener('DOMContentLoaded', () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) entry.target.classList.add('is-visible');
    });
  }, { threshold: 0.08 });
  document.querySelectorAll('.reveal-card').forEach(el => observer.observe(el));

  document.querySelectorAll('.btn-primary, .btn-secondary, .btn-small').forEach(btn => {
    btn.addEventListener('click', function(e){
      const r = document.createElement('span');
      r.className = 'btn-ripple';
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      r.style.width = r.style.height = size + 'px';
      r.style.left = (e.clientX - rect.left - size / 2) + 'px';
      r.style.top = (e.clientY - rect.top - size / 2) + 'px';
      this.appendChild(r);
      setTimeout(() => r.remove(), 700);
    });
  });

  const addPointBtn = document.querySelector('[data-add-point]');
  const pointsWrap = document.querySelector('[data-points-wrap]');
  if (addPointBtn && pointsWrap) {
    addPointBtn.addEventListener('click', () => {
      const count = pointsWrap.querySelectorAll('[data-point-row]').length + 1;
      const row = document.createElement('div');
      row.className = 'grid gap-3 md:grid-cols-[90px_1fr_auto] items-start reveal-card is-visible';
      row.setAttribute('data-point-row', '');
      row.innerHTML = `
        <div class="order-badge">${count}</div>
        <input type="text" name="texte[]" placeholder="Nouveau point de contrôle" required>
        <button type="button" class="btn-secondary" data-remove-point>Retirer</button>
      `;
      pointsWrap.appendChild(row);
    });
    pointsWrap.addEventListener('click', (e) => {
      if (e.target.matches('[data-remove-point]')) {
        const row = e.target.closest('[data-point-row]');
        if (row && pointsWrap.querySelectorAll('[data-point-row]').length > 1) row.remove();
      }
    });
  }
});
