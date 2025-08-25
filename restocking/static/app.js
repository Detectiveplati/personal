// Header micro-interactions + active nav highlight + brand color control
(function () {
  const header = document.querySelector('[data-header]');
  const navLinks = document.querySelectorAll('[data-nav] [data-route]');
  const root = document.documentElement;

  // Shrink / lift header on scroll
  const setScrolled = () => {
    if (!header) return;
    const scrolled = window.scrollY > 6;
    header.classList.toggle('scrolled', scrolled);
  };
  setScrolled();
  window.addEventListener('scroll', setScrolled, { passive: true });

  // Mark current nav item as active
  const path = window.location.pathname.replace(/\/+$/, '');
  navLinks.forEach(a => {
    const href = a.getAttribute('href')?.replace(/\/+$/, '');
    if (href && (href === path || (href !== '/' && path.startsWith(href)))) {
      a.classList.add('is-active');
    }
  });

  // Optional: set brand shade dynamically (future-proofing if you theme later)
  // root.style.setProperty('--brand-600', '#0b8583');
})();
