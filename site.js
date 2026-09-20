/* ASCF preview build — shared behaviour
   ------------------------------------------------------------------
   ACCESS_CODE  : change before sharing the preview link
   GA_ID        : replace with the real GA4 measurement ID at launch
   ------------------------------------------------------------------ */
var ACCESS_CODE = 'canvas2028';
var GA_ID = 'G-XXXXXXXXXX';

/* ---------- 1. access gate ---------- */
(function () {
  var gate = document.getElementById('gate');
  if (!gate) return;
  function ok() { try { return sessionStorage.getItem('ascf_ok') === '1'; } catch (e) { return false; } }
  function unlock(save) {
    gate.style.display = 'none';
    document.body.classList.remove('locked');
    if (save) { try { sessionStorage.setItem('ascf_ok', '1'); } catch (e) {} }
  }
  document.body.classList.add('locked');
  if (ok()) { unlock(false); return; }
  function attempt() {
    var v = document.getElementById('code').value.trim().toLowerCase();
    if (v === ACCESS_CODE) { unlock(true); }
    else { document.getElementById('gateErr').textContent = "That code isn't right."; }
  }
  document.getElementById('enter').addEventListener('click', attempt);
  document.getElementById('code').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') attempt();
  });
})();

/* ---------- 2. mobile nav ---------- */
(function () {
  var b = document.getElementById('burger'), l = document.getElementById('navLinks');
  if (!b || !l) return;
  b.addEventListener('click', function () {
    var open = l.classList.toggle('open');
    b.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
})();

/* ---------- 3. hero carousel ---------- */
(function () {
  var slides = document.querySelectorAll('.slide');
  var dots = document.querySelectorAll('.dots button');
  if (slides.length < 2) return;
  var i = 0, timer = null;
  var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function show(n) {
    slides[i].classList.remove('on');
    if (dots[i]) dots[i].setAttribute('aria-selected', 'false');
    i = (n + slides.length) % slides.length;
    slides[i].classList.add('on');
    if (dots[i]) dots[i].setAttribute('aria-selected', 'true');
  }
  function play() { if (!still) timer = setInterval(function () { show(i + 1); }, 6000); }
  function stop() { clearInterval(timer); }

  dots.forEach(function (d, n) {
    d.addEventListener('click', function () { stop(); show(n); play(); track('hero_slide_' + (n + 1)); });
  });
  var hero = document.querySelector('.hero');
  if (hero) {
    hero.addEventListener('mouseenter', stop);
    hero.addEventListener('mouseleave', play);
  }
  play();
})();

/* ---------- 4. click analytics ----------
   Every element with data-track fires a GA4 event and is counted
   locally so the tracking can be demonstrated without a live GA
   property connected. Local counts are preview-only. */
function track(name, extra) {
  var payload = Object.assign({ label: name, page: document.title }, extra || {});
  if (typeof gtag === 'function') { gtag('event', 'ascf_click', payload); }
  try {
    var k = 'ascf_clicks';
    var d = JSON.parse(localStorage.getItem(k) || '{}');
    d[name] = (d[name] || 0) + 1;
    localStorage.setItem(k, JSON.stringify(d));
  } catch (e) {}
  if (window.console) console.log('[track]', name, payload);
  renderClicks();
}

document.addEventListener('click', function (e) {
  var el = e.target.closest('[data-track]');
  if (el) track(el.getAttribute('data-track'));
});

function renderClicks() {
  var box = document.getElementById('clickList');
  if (!box) return;
  var d = {};
  try { d = JSON.parse(localStorage.getItem('ascf_clicks') || '{}'); } catch (e) {}
  var keys = Object.keys(d).sort(function (a, b) { return d[b] - d[a]; });
  if (!keys.length) {
    box.innerHTML = '<span class="none">No clicks recorded yet. Use the site, then reopen this panel.</span>';
    return;
  }
  box.innerHTML = keys.map(function (k) {
    var row = document.createElement('div');
    var s = document.createElement('span'); s.textContent = k;
    var b = document.createElement('b'); b.textContent = d[k];
    row.appendChild(s); row.appendChild(b);
    return row.outerHTML;
  }).join('');
}

/* ---------- 5. analytics panel ---------- */
(function () {
  var fab = document.getElementById('fab'), panel = document.getElementById('panel');
  if (!fab || !panel) return;
  fab.addEventListener('click', function () { panel.classList.add('open'); renderClicks(); });
  var x = document.getElementById('panelClose');
  if (x) x.addEventListener('click', function () { panel.classList.remove('open'); });
  var clr = document.getElementById('clearClicks');
  if (clr) clr.addEventListener('click', function () {
    try { localStorage.removeItem('ascf_clicks'); } catch (e) {}
    renderClicks();
  });
  renderClicks();
})();

/* ---------- 6. forms (preview: no backend yet) ---------- */
document.addEventListener('submit', function (e) {
  var f = e.target;
  if (!f.hasAttribute('data-demo')) return;
  e.preventDefault();
  track('submit_' + (f.getAttribute('data-track-form') || 'form'));
  var msg = f.getAttribute('data-ok') || "You're on the list. We'll be in touch.";
  var out = document.createElement('p');
  out.className = 'ok';
  out.textContent = msg;
  f.replaceWith(out);
});
