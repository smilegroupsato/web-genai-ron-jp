(() => {
  const KEY = 'genai-ron-appearance';
  const TEXT_SIZE_KEY = 'genai-ron-article-text-size';
  const THEMES = ['paper', 'reading', 'archive'];
  const LABELS = { paper: 'Paper', reading: 'Reading', archive: 'Archive' };
  const TEXT_SIZES = ['small', 'normal', 'large', 'x-large'];
  const TEXT_LABELS = {
    small: '小',
    normal: '標準',
    large: '大',
    'x-large': '特大'
  };

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

  function getStoredTextSize() {
    try {
      const value = localStorage.getItem(TEXT_SIZE_KEY);
      return TEXT_SIZES.includes(value) ? value : 'normal';
    } catch (_) {
      return 'normal';
    }
  }

  function setTextSize(size, persist = true) {
    const next = TEXT_SIZES.includes(size) ? size : 'normal';
    document.documentElement.dataset.articleTextSize = next;
    if (persist) {
      try { localStorage.setItem(TEXT_SIZE_KEY, next); } catch (_) {}
    }
    document.querySelectorAll('[data-article-text-size-choice]').forEach((button) => {
      const active = button.dataset.articleTextSizeChoice === next;
      button.setAttribute('aria-pressed', String(active));
      if (active) {
        button.setAttribute('aria-current', 'true');
      } else {
        button.removeAttribute('aria-current');
      }
    });
  }

  function shouldMountTextSizeControl() {
    if (!document.body || !document.body.classList.contains('series-page')) {
      return false;
    }
    if (!document.querySelector('.series-main > article.note-box')) {
      return false;
    }
    const path = window.location.pathname;
    return path.includes('/series/genai-shikumi/') || path.includes('/series/genai-shikumi-technical/');
  }

  function mountTextSizeControl() {
    setTextSize(getStoredTextSize(), false);
    if (!shouldMountTextSizeControl() || document.querySelector('.article-text-size-control')) {
      return;
    }

    const seriesMain = document.querySelector('.series-main');
    const article = document.querySelector('.series-main > article.note-box');
    if (!seriesMain || !article) {
      return;
    }

    const control = document.createElement('section');
    control.className = 'article-text-size-control';
    control.setAttribute('aria-label', '記事本文の文字サイズ');

    const label = document.createElement('span');
    label.className = 'article-text-size-label';
    label.textContent = '文字サイズ';
    control.appendChild(label);

    const group = document.createElement('div');
    group.className = 'article-text-size-options';
    group.setAttribute('role', 'group');
    group.setAttribute('aria-label', '記事本文の文字サイズを選択');

    TEXT_SIZES.forEach((size) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'article-text-size-button';
      button.textContent = TEXT_LABELS[size];
      button.dataset.articleTextSizeChoice = size;
      button.setAttribute('aria-label', `記事本文の文字サイズを${TEXT_LABELS[size]}にする`);
      button.setAttribute('aria-pressed', 'false');
      button.addEventListener('click', () => setTextSize(size));
      group.appendChild(button);
    });

    control.appendChild(group);
    seriesMain.insertBefore(control, article);
    setTextSize(getStoredTextSize(), false);
  }

  function mountSwitcher() {
    if (document.querySelector('.appearance-switcher')) {
      setTheme(getStoredTheme());
      return;
    }

    const switcher = document.createElement('div');
    switcher.className = 'appearance-switcher';
    switcher.setAttribute('role', 'group');
    switcher.setAttribute('aria-label', 'Appearance');

    THEMES.forEach((theme) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = LABELS[theme];
      button.dataset.appearanceChoice = theme;
      button.setAttribute('aria-pressed', 'false');
      button.addEventListener('click', () => setTheme(theme));
      switcher.appendChild(button);
    });

    document.body.appendChild(switcher);
    setTheme(getStoredTheme());
  }

  setTheme(getStoredTheme());
  setTextSize(getStoredTextSize(), false);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      mountSwitcher();
      mountTextSizeControl();
    });
  } else {
    mountSwitcher();
    mountTextSizeControl();
  }
})();
