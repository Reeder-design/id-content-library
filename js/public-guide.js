(() => {
  const drawer = document.querySelector('[data-public-guide]');
  if (!drawer) return;

  const scrim = document.querySelector('[data-public-guide-scrim]');
  const openers = [...document.querySelectorAll('[data-public-guide-open]')];
  const closers = [...document.querySelectorAll('[data-public-guide-close]')];
  let lastFocused = null;

  const closeGuide = () => {
    drawer.classList.remove('is-open');
    drawer.setAttribute('aria-hidden', 'true');
    if (scrim) scrim.hidden = true;
    document.body.classList.remove('public-guide-open');
    if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
  };

  const openGuide = (event) => {
    lastFocused = event?.currentTarget || document.activeElement;
    drawer.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');
    if (scrim) scrim.hidden = false;
    document.body.classList.add('public-guide-open');
    const closeButton = drawer.querySelector('[data-public-guide-close]');
    if (closeButton) closeButton.focus();
  };

  openers.forEach((button) => button.addEventListener('click', openGuide));
  closers.forEach((button) => button.addEventListener('click', closeGuide));
  if (scrim) scrim.addEventListener('click', closeGuide);

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && drawer.classList.contains('is-open')) closeGuide();
  });
})();
