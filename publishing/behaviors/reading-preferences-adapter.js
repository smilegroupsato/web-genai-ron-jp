(() => {
  /**
   * Transitional adapter for the structured publishing preview.
   *
   * The current public theme.js still creates the controls. This adapter owns only
   * their placement, moving them into a dedicated component instead of leaving
   * runtime-created UI as a direct child of body or coupling it to the article.
   */
  function mountReadingPreferences() {
    const slot = document.querySelector('[data-reading-preferences-slot]');
    if (!slot) return;

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
