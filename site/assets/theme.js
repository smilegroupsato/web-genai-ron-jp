(() => {
  const KEY = 'genai-ron-appearance';
  const THEMES = ['paper', 'reading', 'archive'];
  const LABELS = { paper: 'Paper', reading: 'Reading', archive: 'Archive' };

  function getStoredTheme() {
    try {
      const value = localStorage.getItem(KEY);
      return THEMES.includes(value) ? value : 'paper';
    } catch (_) {
      return 'paper';
    }
  }

  function setTheme(theme) {
    const next = THEMES.includes(theme) ? theme : 'paper';
    document.documentElement.dataset.appearance = next;
    try { localStorage.setItem(KEY, next); } catch (_) {}
    document.querySelectorAll('[data-appearance-choice]').forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.appearanceChoice === next));
    });
  }

  function mountSwitcher() {
    if (document.querySelector('.appearance-switcher')) return;
    const switcher = document.createElement('div');
    switcher.className = 'appearance-switcher';
    switcher.setAttribute('role', 'group');
    switcher.setAttribute('aria-label', '表示テーマ');

    THEMES.forEach((theme) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = LABELS[theme];
      button.dataset.appearanceChoice = theme;
      button.addEventListener('click', () => setTheme(theme));
      switcher.appendChild(button);
    });

    document.body.appendChild(switcher);
    setTheme(getStoredTheme());
  }

  setTheme(getStoredTheme());
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountSwitcher);
  } else {
    mountSwitcher();
  }
})();
