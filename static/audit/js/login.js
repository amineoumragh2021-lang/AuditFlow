document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.password-toggle');
  const password = document.getElementById('login-password');
  if (!toggle || !password) return;
  toggle.hidden = false;
  toggle.addEventListener('click', () => {
    const visible = password.type === 'password';
    password.type = visible ? 'text' : 'password';
    toggle.setAttribute('aria-pressed', String(visible));
    toggle.setAttribute('aria-label', visible ? 'Masquer le mot de passe' : 'Afficher le mot de passe');
  });
});
