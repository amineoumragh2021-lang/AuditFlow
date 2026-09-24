document.addEventListener('DOMContentLoaded', () => {
  const password = document.getElementById('id_password');
  const toggle = document.querySelector('.register-password-toggle');
  if (!password || !toggle) return;
  password.autocomplete = 'new-password';
  toggle.hidden = false;
  toggle.addEventListener('click', () => {
    const visible = password.type === 'password';
    password.type = visible ? 'text' : 'password';
    toggle.setAttribute('aria-pressed', String(visible));
    toggle.setAttribute('aria-label', visible ? 'Masquer le mot de passe' : 'Afficher le mot de passe');
  });
});
