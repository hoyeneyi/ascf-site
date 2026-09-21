/* ===========================================================
   ASCF — shared behaviour
   Mobile nav · hero carousel · analytics · email capture
   =========================================================== */
(function () {
  'use strict';

  /* ---------- 1. Analytics ------------------------------------------
     Google Analytics 4 loads from the <head> of each page.
     Replace G-XXXXXXXXXX in assets/js/analytics.js with the real ID.
     Any element with data-track fires an event on click, so the client
     can see exactly which buttons and links people use.
  ------------------------------------------------------------------ */
  function track(name, params) {
    try {
      if (typeof window.gtag === 'function') {
        window.gtag('event', name, params || {});
      }
      if (window.ASCF_DEBUG) console.log('[track]', name, params || {});
    } catch (e) {}
  }
  window.ascfTrack = track;

  document.addEventListener('click', function (e) {
    var el = e.target.closest('[data-track]');
    if (!el) return;
    track(el.getAttribute('data-track'), {
      label: (el.getAttribute('data-label') || el.textContent || '').trim().slice(0, 80),
      page: document.body.getAttribute('data-page') || location.pathname
    });
  });

  /* Scroll depth — tells the client how far down pages people actually get */
  var marks = [25, 50, 75, 100], hit = {};
  window.addEventListener('scroll', function () {
    var h = document.documentElement;
    var pct = ((h.scrollTop + window.innerHeight) / h.scrollHeight) * 100;
    marks.forEach(function (m) {
      if (pct >= m && !hit[m]) { hit[m] = 1; track('scroll_depth', { percent: m }); }
    });
  }, { passive: true });

  /* ---------- 2. Mobile nav ---------------------------------------- */
  var toggle = document.querySelector('.navtoggle');
  var menu = document.querySelector('.mobilemenu');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      track('nav_toggle', { state: open ? 'open' : 'closed' });
    });
  }

  /* ---------- 3. Hero carousel ------------------------------------- */
  var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));
  var dotWrap = document.querySelector('.dots');
  if (slides.length > 1 && dotWrap) {
    var i = 0, timer = null;
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    slides.forEach(function (s, n) {
      var b = document.createElement('button');
      b.setAttribute('aria-label', 'Slide ' + (n + 1));
      if (n === 0) b.className = 'on';
      b.addEventListener('click', function () { go(n); restart(); track('hero_dot', { slide: n + 1 }); });
      dotWrap.appendChild(b);
    });
    var dots = Array.prototype.slice.call(dotWrap.children);

    function go(n) {
      slides[i].classList.remove('on'); dots[i].classList.remove('on');
      i = (n + slides.length) % slides.length;
      slides[i].classList.add('on'); dots[i].classList.add('on');
    }
    function restart() { if (timer) clearInterval(timer); if (!reduce) timer = setInterval(function () { go(i + 1); }, 6500); }
    restart();

    var hero = document.querySelector('.hero');
    hero.addEventListener('mouseenter', function () { if (timer) clearInterval(timer); });
    hero.addEventListener('mouseleave', restart);

    /* swipe on touch */
    var x0 = null;
    hero.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    hero.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 45) { go(i + (dx < 0 ? 1 : -1)); restart(); track('hero_swipe', {}); }
      x0 = null;
    }, { passive: true });
  }

  /* ---------- 4. Email capture -------------------------------------
     Swap the Formspree endpoint below for the client's real form ID.
     Until then submissions are logged, not sent.
  ------------------------------------------------------------------ */
  var FORM_ENDPOINT = ''; /* e.g. 'https://formspree.io/f/xxxxxxxx' */

  document.querySelectorAll('form[data-signup]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = form.querySelector('input[type=email]');
      if (!input || !input.value.trim()) return;
      var where = form.getAttribute('data-signup');

      track('email_signup', { location: where });

      function done() {
        var note = form.parentNode.querySelector('.signup-note, .ok');
        if (note) { note.style.display = 'block'; note.textContent = "You're on the list."; }
        form.reset();
      }

      if (!FORM_ENDPOINT) { done(); return; }
      fetch(FORM_ENDPOINT, {
        method: 'POST',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: input.value.trim(), source: where })
      }).then(done).catch(done);
    });
  });

  /* ---------- 5. Admin-editable content ----------------------------
     Any element with data-edit="key" is overwritten by whatever the
     admin portal has saved for that key. Demo storage is localStorage;
     production swaps this one function for a Firestore read.
  ------------------------------------------------------------------ */
  function loadContent() {
    var data = {};
    try { data = JSON.parse(localStorage.getItem('ascf_content') || '{}'); } catch (e) { return; }
    Object.keys(data).forEach(function (key) {
      document.querySelectorAll('[data-edit="' + key + '"]').forEach(function (el) {
        el.textContent = data[key];
      });
    });
  }
  loadContent();

  /* Lineup published from the admin portal */
  function loadLineup() {
    var host = document.getElementById('lineupLive');
    var empty = document.getElementById('lineupEmpty');
    if (!host) return;
    var acts = [];
    try { acts = JSON.parse(localStorage.getItem('ascf_lineup') || '[]'); } catch (e) { return; }
    if (!acts.length) return;
    host.innerHTML = '';
    acts.forEach(function (a) {
      var row = document.createElement('div');
      row.className = 'row';
      var b = document.createElement('b'); b.textContent = a.name;
      var s = document.createElement('small'); s.textContent = (a.stage || '') + ' · ' + (a.time || '');
      row.appendChild(b); row.appendChild(s);
      host.appendChild(row);
    });
    host.style.display = 'block';
    if (empty) empty.style.display = 'none';
  }
  loadLineup();
})();
