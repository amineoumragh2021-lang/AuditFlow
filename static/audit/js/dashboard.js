document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-auto-submit]').forEach(select => {
    select.addEventListener('change', () => select.form.requestSubmit());
  });
  document.addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      document.querySelector('.header-search input')?.focus();
    }
    if (event.key === 'Escape') document.querySelector('.notification-menu')?.removeAttribute('open');
  });
  const search = document.getElementById('mission-search');
  const filter = document.getElementById('mission-filter');
  const rows = [...document.querySelectorAll('[data-mission-row]')];
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('fr');
  function filterMissions() {
    const query = normalize(search.value.trim());
    let count = 0;
    rows.forEach(row => {
      const visible = normalize(row.textContent).includes(query) && (!filter.value || row.dataset.state === filter.value);
      row.hidden = !visible;
      if (visible) count++;
    });
    document.getElementById('mission-count').textContent = `${count} mission${count === 1 ? '' : 's'}`;
    document.getElementById('no-mission-results').hidden = count > 0 || rows.length === 0;
  }
  search.addEventListener('input', filterMissions);
  filter.addEventListener('change', filterMissions);
  const tabs = [...document.querySelectorAll('[data-tab]')];
  function activateTab(selected) {
    tabs.forEach(tab => {
      const active = tab === selected;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      document.getElementById(tab.dataset.tab).hidden = !active;
    });
    search.closest('label').hidden = selected.dataset.tab !== 'mission-content';
    filter.hidden = selected.dataset.tab !== 'mission-content';
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(tab));
    tab.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
      activateTab(tabs[next]);
      tabs[next].focus();
    });
  });
});
