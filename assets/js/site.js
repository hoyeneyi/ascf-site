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
  var navEl = document.querySelector('.nav');

  function closeMenu() {
    if (!menu) return;
    menu.classList.remove('open');
    menu.style.top = '';
    document.body.classList.remove('menu-open');
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
  }

  function openMenu() {
    if (!menu || !navEl) return;
    /* Pin the panel directly under the header and let it scroll on its own.
       Without this the menu is taller than the viewport, which breaks the
       sticky header and makes the whole page scroll instead. */
    menu.style.top = Math.max(0, navEl.getBoundingClientRect().bottom) + 'px';
    menu.classList.add('open');
    document.body.classList.add('menu-open');
    if (toggle) toggle.setAttribute('aria-expanded', 'true');
  }

  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var isOpen = menu.classList.contains('open');
      if (isOpen) { closeMenu(); } else { openMenu(); }
      track('nav_toggle', { state: isOpen ? 'closed' : 'open' });
    });

    /* tapping a link closes the panel so the next page isn't covered */
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeMenu();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });

    /* rotating the phone or resizing to desktop shouldn't strand it */
    window.addEventListener('resize', function () {
      if (!menu.classList.contains('open')) return;
      if (window.innerWidth >= 900) { closeMenu(); }
      else { menu.style.top = Math.max(0, navEl.getBoundingClientRect().bottom) + 'px'; }
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
    function restart() {
      if (timer) clearInterval(timer);
      var d = dots[i];
      d.classList.remove('on'); void d.offsetWidth; d.classList.add('on');
      if (!reduce) timer = setInterval(function () { go(i + 1); }, 6500);
    }
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

  /* ---------- 5. Editable content lives in content.js ---------- */

  /* ---------- 6. Scroll reveal ------------------------------------
     Only elements that start below the fold get hidden, so nothing
     already on screen ever flashes out and back in.
  ------------------------------------------------------------------ */
  (function () {
    if (!('IntersectionObserver' in window)) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var sel = 'section .section-head, .cards > *, .grid > *, .split > *, .mission-box, ' +
              '.rows .row, .empty, .contact-card, .countdown .wrap, .band .wrap';
    var els = Array.prototype.slice.call(document.querySelectorAll(sel));
    var fold = window.innerHeight;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    var groupIdx = new Map();
    els.forEach(function (el) {
      if (el.getBoundingClientRect().top < fold) return;
      var parent = el.parentElement;
      var n = groupIdx.get(parent) || 0;
      groupIdx.set(parent, n + 1);
      el.style.transitionDelay = (Math.min(n, 5) * 70) + 'ms';
      el.classList.add('rv');
      io.observe(el);
    });
  })();

  /* ---------- 7. Count-up stats ------------------------------------ */
  (function () {
    if (!('IntersectionObserver' in window)) return;
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var nodes = document.querySelectorAll('.stat span, .execute .items span');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        io.unobserve(en.target);
        var el = en.target, raw = el.getAttribute('data-final');
        var m = raw.match(/^(\D*)([\d,]+)(.*)$/);
        if (!m) return;
        var pre = m[1], target = parseInt(m[2].replace(/,/g, ''), 10), post = m[3];
        var commas = m[2].indexOf(',') > -1;
        var t0 = null, dur = Math.min(1600, 700 + target / 40);
        function fmt(v) { return commas ? v.toLocaleString('en-US') : String(v); }
        function step(ts) {
          if (!t0) t0 = ts;
          var k = Math.min(1, (ts - t0) / dur);
          var eased = 1 - Math.pow(1 - k, 3);
          el.textContent = pre + fmt(Math.round(target * eased)) + post;
          if (k < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
      });
    }, { threshold: 0.4 });
    Array.prototype.forEach.call(nodes, function (el) {
      var txt = el.textContent.trim();
      el.setAttribute('data-final', txt);
      if (reduce || !/\d/.test(txt)) return;
      io.observe(el);
    });
  })();

  /* ---------- 8. Countdown ----------------------------------------- 
     Gates open Friday May 26, 2028 at noon, Eastern (UTC-4 in May).
  ------------------------------------------------------------------ */
  (function () {
    var box = document.getElementById('countdown');
    if (!box) return;
    var OPEN = Date.UTC(2028, 4, 26, 16, 0, 0);
    var d = box.querySelector('[data-u="d"]'), h = box.querySelector('[data-u="h"]'),
        m = box.querySelector('[data-u="m"]'), s = box.querySelector('[data-u="s"]');
    function pad(n) { return n < 10 ? '0' + n : String(n); }
    function tick() {
      var left = Math.max(0, OPEN - Date.now());
      var sec = Math.floor(left / 1000);
      d.textContent = Math.floor(sec / 86400).toLocaleString('en-US');
      h.textContent = pad(Math.floor(sec % 86400 / 3600));
      m.textContent = pad(Math.floor(sec % 3600 / 60));
      s.textContent = pad(sec % 60);
    }
    tick();
    setInterval(tick, 1000);
  })();

  /* ---------- 9. Back to top --------------------------------------- */
  var top = document.querySelector('.totop');
  if (top) top.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    track('back_to_top', {});
  });
})();
