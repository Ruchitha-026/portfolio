(() => {
  const menuButton = document.querySelector('.menu-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (menuButton && navLinks) {
    menuButton.addEventListener('click', () => {
      const open = navLinks.classList.toggle('open');
      menuButton.setAttribute('aria-expanded', String(open));
    });
    navLinks.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
      navLinks.classList.remove('open');
      menuButton.setAttribute('aria-expanded', 'false');
    }));
  }

  const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, {threshold: 0.1});
  document.querySelectorAll('.reveal').forEach(element => revealObserver.observe(element));

  document.querySelectorAll('[data-tabs]').forEach(shell => {
    const tabs = [...shell.querySelectorAll('[data-tab-target]')];
    const panels = [...shell.querySelectorAll('[data-tab-panel]')];

    const activate = target => {
      tabs.forEach(tab => {
        const active = tab.dataset.tabTarget === target;
        tab.classList.toggle('active', active);
        tab.setAttribute('aria-selected', String(active));
      });
      panels.forEach(panel => panel.classList.toggle('active', panel.dataset.tabPanel === target));
      history.replaceState(null, '', `#${target}`);
    };

    tabs.forEach(tab => tab.addEventListener('click', () => activate(tab.dataset.tabTarget)));
    const requested = location.hash.replace('#', '');
    if (requested && panels.some(panel => panel.dataset.tabPanel === requested)) activate(requested);
  });
})();
