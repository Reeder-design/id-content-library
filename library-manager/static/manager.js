(() => {
  const guideDrawer = document.querySelector('[data-guide-drawer]');
  const guideScrim = document.querySelector('[data-guide-scrim]');
  const openGuide = () => {
    if (!guideDrawer || !guideScrim) return;
    guideDrawer.classList.add('open');
    guideDrawer.setAttribute('aria-hidden', 'false');
    guideScrim.hidden = false;
    document.body.classList.add('guide-open');
  };
  const closeGuide = () => {
    if (!guideDrawer || !guideScrim) return;
    guideDrawer.classList.remove('open');
    guideDrawer.setAttribute('aria-hidden', 'true');
    guideScrim.hidden = true;
    document.body.classList.remove('guide-open');
  };
  document.querySelectorAll('[data-guide-open]').forEach((button) => button.addEventListener('click', openGuide));
  document.querySelectorAll('[data-guide-close]').forEach((button) => button.addEventListener('click', closeGuide));
  if (guideScrim) guideScrim.addEventListener('click', closeGuide);
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeGuide();
  });

  const search = document.querySelector('#library-search');
  if (search) {
    const cards = [...document.querySelectorAll('[data-library-card]')];
    const count = document.querySelector('#result-count');
    const applySearch = () => {
      const query = search.value.trim().toLowerCase();
      let visible = 0;
      cards.forEach((card) => {
        const matches = !query || (card.dataset.search || '').includes(query);
        card.hidden = !matches;
        if (matches) visible += 1;
      });
      if (count) count.textContent = `${visible} item(s)`;
    };
    search.addEventListener('input', applySearch);
  }

})();
