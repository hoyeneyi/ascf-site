/* ===========================================================
   ASCF — Coming Soon gate
   Decides, before anything is painted, whether this visitor sees the
   real site or the Coming Soon page.

   The Coming Soon markup is already in every built page, hidden by
   CSS, so the fall-back still works if this file never loads. An
   inline script in <head> hides the document and, after 2 seconds,
   applies COMING_SOON_DEFAULT from build.py.

   This hides the site from casual visitors. It is not a security
   lock: the page HTML is public either way.
   =========================================================== */
(function () {
  'use strict';

  var d = document.documentElement;
  var CFG = window.ASCF_FIREBASE || null;
  var STORE = 'ascf_preview_hash';
  var settled = false;

  function settle(showComingSoon) {
    if (settled) return;
    settled = true;
    if (window.__ascfGateTimer) clearTimeout(window.__ascfGateTimer);
    d.classList.remove('ascf-gate-wait');
    if (showComingSoon) { d.classList.add('ascf-cs'); } else { d.classList.remove('ascf-cs'); }
    document.dispatchEvent(new CustomEvent('ascf:gate', { detail: { comingSoon: !!showComingSoon } }));
  }

  /* This file runs in <head>, so the Coming Soon markup may not be parsed
     yet when the settings resolve. The class toggle has to stay immediate
     (that is what prevents the flash), but anything touching the DOM waits. */
  function onReady(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  function forced() {
    return /[?&]preview=comingsoon(&|$)/.test(location.search);
  }

  /* SHA-256 hex. Needs a secure context; localhost and https both are. */
  function sha256(text) {
    if (!(window.crypto && window.crypto.subtle)) return Promise.resolve('');
    return window.crypto.subtle.digest('SHA-256', new TextEncoder().encode(text))
      .then(function (buf) {
        return Array.prototype.map.call(new Uint8Array(buf), function (b) {
          return ('0' + b.toString(16)).slice(-2);
        }).join('');
      });
  }

  function readSettings() {
    if (!CFG) {
      try {
        var c = JSON.parse(localStorage.getItem('ascf_demo_content') || 'null');
        return Promise.resolve((c && c.settings) || null);
      } catch (e) { return Promise.resolve(null); }
    }
    var url = 'https://firestore.googleapis.com/v1/projects/' +
              encodeURIComponent(CFG.projectId) +
              '/databases/(default)/documents/site/content';
    return fetch(url).then(function (r) {
      /* 404 means Site status has never been published. Treat that as
         "no decision yet" and use COMING_SOON_DEFAULT, so a brand new
         deployment stays closed rather than opening itself. */
      if (!r.ok) return null;
      return r.json().then(function (j) {
        var sf = j.fields && j.fields.settings && j.fields.settings.mapValue;
        if (!sf) return null;
        var f = sf.fields || {};
        return {
          comingSoon: !!(f.comingSoon && f.comingSoon.booleanValue),
          previewCodeHash: (f.previewCodeHash && f.previewCodeHash.stringValue) || '',
          comingSoonHeadline: (f.comingSoonHeadline && f.comingSoonHeadline.stringValue) || '',
          comingSoonMessage: (f.comingSoonMessage && f.comingSoonMessage.stringValue) || ''
        };
      });
    });
  }

  function paint(s) {
    var h = document.getElementById('cs-headline');
    var m = document.getElementById('cs-message');
    if (h && s.comingSoonHeadline) h.textContent = s.comingSoonHeadline;
    if (m && s.comingSoonMessage) m.textContent = s.comingSoonMessage;
  }

  function wireUnlock(s) {
    var toggle = document.getElementById('cs-codetoggle');
    var wrap = document.getElementById('cs-codewrap');
    var input = document.getElementById('cs-code');
    var go = document.getElementById('cs-codego');
    var msg = document.getElementById('cs-codemsg');
    if (!toggle || !wrap || !input || !go) return;

    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      var open = wrap.style.display === 'block';
      wrap.style.display = open ? 'none' : 'block';
      toggle.setAttribute('aria-expanded', open ? 'false' : 'true');
      if (!open) input.focus();
    });

    function tryCode() {
      var v = input.value.trim();
      if (!v) return;
      if (!s.previewCodeHash) { msg.textContent = 'No preview code has been set yet.'; return; }
      sha256(v).then(function (hex) {
        if (hex && hex === s.previewCodeHash) {
          try { localStorage.setItem(STORE, hex); } catch (e) {}
          location.href = location.pathname + location.hash;
        } else {
          msg.textContent = 'That code does not match.';
          input.select();
        }
      });
    }
    go.addEventListener('click', tryCode);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); tryCode(); }
    });
  }

  /* The Coming Soon signup writes the same shape as the other forms. */
  function wireSignup() {
    var form = document.getElementById('cs-signup');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = form.querySelector('input[type=email]');
      var note = document.getElementById('cs-signupnote');
      var btn = form.querySelector('button');
      if (!input) return;
      var email = input.value.trim().toLowerCase();

      function say(t, err) {
        if (!note) return;
        note.style.display = 'block';
        note.textContent = t;
        if (err) { note.classList.add('signup-err'); } else { note.classList.remove('signup-err'); }
      }
      function done(ok) {
        if (btn) { btn.disabled = false; btn.style.opacity = ''; }
        if (ok) { say('You are on the list.', false); form.reset(); }
        else { say('Something went wrong, please try again.', true); }
      }
      if (email.length > 254 || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { done(false); return; }
      if (btn) { btn.disabled = true; btn.style.opacity = '.6'; }

      var rec = {
        email: email,
        source: 'coming_soon',
        page: location.pathname.slice(0, 200),
        createdAt: new Date().toISOString()
      };
      if (!CFG) {
        try {
          var all = JSON.parse(localStorage.getItem('ascf_signups') || '[]');
          all.push(rec);
          localStorage.setItem('ascf_signups', JSON.stringify(all));
          done(true);
        } catch (err) { done(false); }
        return;
      }
      fetch('https://firestore.googleapis.com/v1/projects/' + encodeURIComponent(CFG.projectId) +
            '/databases/(default)/documents/signups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fields: {
          email: { stringValue: rec.email },
          source: { stringValue: rec.source },
          page: { stringValue: rec.page },
          createdAt: { timestampValue: rec.createdAt }
        } })
      }).then(function (r) { done(r.ok); }).catch(function () { done(false); });
    });
  }

  readSettings().then(function (s) {
    /* null = nothing published yet, so fall back to the build-time default */
    if (!s) s = { comingSoon: !!window.ASCF_COMING_SOON_DEFAULT };
    var unlocked = false;
    try { unlocked = !!s.previewCodeHash && localStorage.getItem(STORE) === s.previewCodeHash; }
    catch (e) { unlocked = false; }
    var show = forced() || (!!s.comingSoon && !unlocked);
    settle(show);
    onReady(function () {
      paint(s);
      if (show) { wireUnlock(s); wireSignup(); }
    });
  }).catch(function () {
    var show = !!window.ASCF_COMING_SOON_DEFAULT || forced();
    settle(show);
    onReady(function () {
      if (show) { wireUnlock({}); wireSignup(); }
    });
  });
})();
