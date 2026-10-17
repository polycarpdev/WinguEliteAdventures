/* Cockpit: instant navigation + small UI behaviours. No dependencies. */
(() => {
  const cache = new Map();
  const SAME = (a) =>
    a.origin === location.origin && a.pathname.startsWith('/cockpit/') && !a.hasAttribute('download') &&
    !a.target && !a.dataset.reload && !a.pathname.endsWith('.csv') && !a.pathname.includes('/logout');

  const fetchPage = (url) => {
    if (!cache.has(url)) {
      cache.set(url, fetch(url, { credentials: 'same-origin', headers: { 'X-Cockpit-Nav': '1' } })
        .then((r) => (r.ok && r.headers.get('content-type')?.includes('text/html') && !r.redirected ? r.text() : null))
        .catch(() => null));
      setTimeout(() => cache.delete(url), 15000); // keep data fresh
    }
    return cache.get(url);
  };

  const scriptsOf = (doc) => [...doc.querySelectorAll('script[src]')].map((s) => s.src).sort().join('|');

  async function go(url, push = true) {
    const html = await fetchPage(url);
    if (!html) return location.assign(url);
    const doc = new DOMParser().parseFromString(html, 'text/html');
    // Pages with different scripts (e.g. the rich-text editor) get a real load.
    if (!doc.querySelector('.ck-shell') || scriptsOf(doc) !== scriptsOf(document)) return location.assign(url);
    const swap = () => {
      document.title = doc.title;
      document.querySelector('.ck-shell').replaceWith(doc.querySelector('.ck-shell'));
      if (push) history.pushState({ ck: 1 }, '', url);
      window.scrollTo(0, 0);
      init();
    };
    document.startViewTransition ? document.startViewTransition(swap) : swap();
    cache.clear();
  }

  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href]');
    if (!a || e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || !SAME(a)) return;
    e.preventDefault();
    go(a.href);
  });
  const warm = (e) => {
    const a = e.target.closest?.('a[href]');
    if (a && SAME(a)) fetchPage(a.href);
  };
  document.addEventListener('mouseover', warm, { passive: true });
  document.addEventListener('touchstart', warm, { passive: true });
  window.addEventListener('popstate', () => go(location.href, false));
  history.replaceState({ ck: 1 }, '');

  function init() {
    window.onbeforeunload = null;
    // Mobile sidebar
    const side = document.querySelector('[data-side]');
    document.querySelectorAll('[data-side-toggle]').forEach((b) =>
      b.addEventListener('click', () => side?.toggleAttribute('data-open')));
    side?.addEventListener('click', (e) => { if (e.target.closest('a')) side.removeAttribute('data-open'); });

    // Auto-submit filters (selects in toolbars)
    document.querySelectorAll('[data-autosubmit]').forEach((el) => el.addEventListener('change', () => el.form.requestSubmit()));

    // Image field live preview
    document.querySelectorAll('.img-field input[type=file]').forEach((input) => {
      input.addEventListener('change', () => {
        const img = input.closest('.img-field').querySelector('.img-field__preview');
        const file = input.files?.[0];
        if (img && file) { img.src = URL.createObjectURL(file); img.hidden = false; }
      });
    });

    // Multi-photo dropzone
    document.querySelectorAll('.dropzone').forEach((zone) => {
      const input = zone.querySelector('input[type=file]');
      const out = zone.querySelector('.dropzone__files');
      const show = () => { out.textContent = input.files.length ? `${input.files.length} photo(s) ready to upload. Click Save` : ''; };
      input.addEventListener('change', show);
      ['dragenter', 'dragover'].forEach((t) => zone.addEventListener(t, (e) => { e.preventDefault(); zone.classList.add('is-over'); }));
      ['dragleave', 'drop'].forEach((t) => zone.addEventListener(t, () => zone.classList.remove('is-over')));
      zone.addEventListener('drop', (e) => { e.preventDefault(); input.files = e.dataTransfer.files; show(); });
    });

    // Warn before leaving a form with unsaved edits
    document.querySelectorAll('form[data-guard]').forEach((form) => {
      let dirty = false;
      form.addEventListener('input', () => (dirty = true));
      form.addEventListener('submit', () => (dirty = false));
      window.onbeforeunload = () => (dirty ? true : undefined);
    });

    // Confirm destructive actions
    document.querySelectorAll('[data-confirm]').forEach((el) =>
      el.addEventListener('click', (e) => { if (!confirm(el.dataset.confirm)) e.preventDefault(); }));

    // Flash messages fade out
    setTimeout(() => document.querySelectorAll('.flash li:not(.error)').forEach((li) => li.remove()), 6000);
  }

  init();
})();
