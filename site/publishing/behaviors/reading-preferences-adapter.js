(() => {
  /**
   * Transitional adapter for structured publishing pages.
   *
   * The current public theme.js creates the appearance controls globally, but
   * only creates article text-size controls for some series. Structured pages
   * own the reading-preferences slot, so this adapter also provides a local
   * fallback text-size control when theme.js does not create one.
   */
  const TEXT_SIZE_KEY = 'genai-ron-article-text-size';
  const TEXT_SIZES = ['small', 'normal', 'large', 'x-large'];
  const TEXT_LABELS = {
    small: '小',
    normal: '標準',
    large: '大',
    'x-large': '特大'
  };

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
    document.documentElement.dataset.readingSize = next;
    if (persist) {
      try { localStorage.setItem(TEXT_SIZE_KEY, next); } catch (_) {}
    }
    document.querySelectorAll('[data-article-text-size-choice]').forEach((button) => {
      const active = button.dataset.articleTextSizeChoice === next;
      button.setAttribute('aria-pressed', String(active));
      if (active) button.setAttribute('aria-current', 'true');
      else button.removeAttribute('aria-current');
    });
  }

  function ensureTextSizeControl() {
    if (document.querySelector('.article-text-size-control')) {
      setTextSize(getStoredTextSize(), false);
      return;
    }

    const seriesMain = document.querySelector('.series-main');
    const article = document.querySelector('.series-main > article.note-box');
    if (!seriesMain || !article) return;

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

  function mountReadingPreferences() {
    const slot = document.querySelector('[data-reading-preferences-slot]');
    if (!slot) return;

    ensureTextSizeControl();

    const controls = [
      document.querySelector('body > .appearance-switcher'),
      document.querySelector('.series-main > .article-text-size-control'),
    ].filter(Boolean);

    controls.forEach((control) => slot.appendChild(control));

    const region = document.querySelector('[data-reading-preferences]');
    if (region) {
      region.hidden = controls.length === 0;
      region.dataset.mountedControls = String(controls.length);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountReadingPreferences);
  } else {
    mountReadingPreferences();
  }
})();