(function(){
  var storageKey = 'genaiRonAppearance';
  var modes = [
    { id: 'paper', label: 'Paper' },
    { id: 'reading', label: 'Reading' },
    { id: 'archive', label: 'Archive' }
  ];

  function getStoredMode(){
    try {
      var saved = window.localStorage.getItem(storageKey);
      return modes.some(function(mode){ return mode.id === saved; }) ? saved : 'paper';
    } catch (error) {
      return 'paper';
    }
  }

  function setMode(modeId){
    var nextMode = modes.some(function(mode){ return mode.id === modeId; }) ? modeId : 'paper';
    document.documentElement.setAttribute('data-appearance', nextMode);
    try { window.localStorage.setItem(storageKey, nextMode); } catch (error) {}
    var buttons = document.querySelectorAll('[data-appearance-mode]');
    buttons.forEach(function(button){
      var active = button.getAttribute('data-appearance-mode') === nextMode;
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
  }

  function mountSwitcher(){
    if (document.querySelector('.appearance-switcher')) {
      setMode(getStoredMode());
      return;
    }

    var switcher = document.createElement('div');
    switcher.className = 'appearance-switcher';
    switcher.setAttribute('role', 'group');
    switcher.setAttribute('aria-label', 'Appearance');

    modes.forEach(function(mode){
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'appearance-switcher__button';
      button.setAttribute('data-appearance-mode', mode.id);
      button.setAttribute('aria-pressed', 'false');
      button.textContent = mode.label;
      button.addEventListener('click', function(){ setMode(mode.id); });
      switcher.appendChild(button);
    });

    document.body.appendChild(switcher);
    setMode(getStoredMode());
  }

  setMode(getStoredMode());

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountSwitcher);
  } else {
    mountSwitcher();
  }
})();
