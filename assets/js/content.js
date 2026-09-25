/* ===========================================================
   ASCF — published content
   Reads what the admin portal saved and applies it to the page.

   Live mode  (firebase-config.js filled in): one lightweight read of
              the Firestore document site/content over REST. No SDK is
              loaded on public pages, so the site stays fast.
   Demo mode  (no config): reads what the demo admin saved in this
              browser, so the portal can be tried before Firebase exists.
   =========================================================== */
(function () {
  'use strict';

  var CFG = window.ASCF_FIREBASE || null;
  var CACHE_KEY = 'ascf_content_cache_v1';
  var CACHE_MS = 60 * 1000;

  /* ---------- formatting: **bold**, line breaks, blank = hide ---------- */
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
  function fmt(s) {
    return esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>');
  }
  function cssUrl(u) {
    return safeUrl(u).replace(/'/g, '%27').replace(/"/g, '%22').replace(/\(/g, '%28')
      .replace(/\)/g, '%29').replace(/\s/g, '%20');
  }
  function safeUrl(u) {
    u = String(u || '').trim();
    if (/^(https?:|mailto:|tel:|\/|\.\.?\/|#|data:image\/)/i.test(u)) return u;
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(u)) return 'mailto:' + u;   // bare email
    if (/^[\w-]+(\.[\w-]+)+/.test(u)) return 'https://' + u;          // bare domain
    return '';
  }

  /* ---------- Firestore REST decoding ---------- */
  function dec(v) {
    if (!v) return null;
    if ('stringValue' in v) return v.stringValue;
    if ('integerValue' in v) return Number(v.integerValue);
    if ('doubleValue' in v) return v.doubleValue;
    if ('booleanValue' in v) return v.booleanValue;
    if ('nullValue' in v) return null;
    if ('timestampValue' in v) return v.timestampValue;
    if ('mapValue' in v) {
      var o = {}, f = v.mapValue.fields || {};
      for (var k in f) o[k] = dec(f[k]);
      return o;
    }
    if ('arrayValue' in v) return (v.arrayValue.values || []).map(dec);
    return null;
  }

  function fromCache() {
    try {
      var c = JSON.parse(sessionStorage.getItem(CACHE_KEY) || 'null');
      if (c && Date.now() - c.t < CACHE_MS) return c.d;
    } catch (e) {}
    return null;
  }
  function toCache(d) {
    try { sessionStorage.setItem(CACHE_KEY, JSON.stringify({ t: Date.now(), d: d })); } catch (e) {}
  }

  function load() {
    if (!CFG) {
      try { return Promise.resolve(JSON.parse(localStorage.getItem('ascf_demo_content') || 'null')); }
      catch (e) { return Promise.resolve(null); }
    }
    var cached = fromCache();
    if (cached) return Promise.resolve(cached);
    var url = 'https://firestore.googleapis.com/v1/projects/' + encodeURIComponent(CFG.projectId) +
              '/databases/(default)/documents/site/content';
    return fetch(url).then(function (r) {
      if (!r.ok) return null;
      return r.json().then(function (j) {
        var d = dec({ mapValue: { fields: j.fields || {} } });
        toCache(d);
        return d;
      });
    }).catch(function () { return null; });
  }

  /* ---------- apply ---------- */
  function applyText(map) {
    Object.keys(map || {}).forEach(function (key) {
      var val = map[key];
      if (val === null || val === undefined) return;
      document.querySelectorAll('[data-edit="' + key + '"]').forEach(function (el) {
        if (String(val).trim() === '') { el.style.display = 'none'; return; }
        el.style.display = '';
        el.innerHTML = fmt(val);
        if (el.hasAttribute('data-final')) el.setAttribute('data-final', el.textContent.trim());
      });
    });
  }

  function applyImages(map) {
    Object.keys(map || {}).forEach(function (key) {
      var url = safeUrl(map[key]);
      if (!url) return;
      document.querySelectorAll('[data-img="' + key + '"]').forEach(function (el) {
        el.style.backgroundImage = "url('" + cssUrl(url) + "')";
        el.classList.add('has-photo');
      });
    });
  }

  function applyLinks(map) {
    Object.keys(map || {}).forEach(function (key) {
      var url = safeUrl(map[key]);
      if (!url) return;
      document.querySelectorAll('[data-link="' + key + '"]').forEach(function (el) {
        el.setAttribute('href', url);
        if (/^https?:/i.test(url) && url.indexOf(location.host) === -1) {
          el.setAttribute('target', '_blank');
          el.setAttribute('rel', 'noopener');
        }
      });
    });
  }

  /* ---------- lists: lineup, news, vendors, sponsors, partners ---------- */
  var RENDER = {
    lineup: function (it) {
      return '<div class="row"><b>' + esc(it.name) + '</b><small>' + esc(it.detail || '') + '</small></div>';
    },
    news: function (it) {
      return '<article class="post">' +
        (it.image ? '<div class="post-img" style="background-image:url(\'' + cssUrl(it.image) + '\')"></div>' : '') +
        '<div class="date">' + esc(it.detail || '') + '</div>' +
        '<h3>' + esc(it.name) + '</h3>' +
        (it.body ? '<p>' + fmt(it.body) + '</p>' : '') +
        (it.link ? '<a class="more-link" href="' + esc(safeUrl(it.link)) + '">READ MORE &rarr;</a>' : '') +
        '</article>';
    },
    vendors: function (it) {
      var tag = it.link ? 'a' : 'div';
      var href = it.link ? ' href="' + esc(safeUrl(it.link)) + '" target="_blank" rel="noopener"' : '';
      return '<' + tag + ' class="card"' + href + '><div class="bar"></div>' +
        (it.image ? '<div class="thumb has-photo" style="background-image:url(\'' + cssUrl(it.image) + '\')"></div>' : '') +
        '<div class="body"><h3>' + esc(it.name) + '</h3>' +
        (it.body ? '<p>' + fmt(it.body) + '</p>' : '') + '</div></' + tag + '>';
    },
    logos: function (it) {
      var tag = it.link ? 'a' : 'div';
      var href = it.link ? ' href="' + esc(safeUrl(it.link)) + '" target="_blank" rel="noopener"' : '';
      var inner = it.image
        ? '<img src="' + esc(safeUrl(it.image)) + '" alt="' + esc(it.name) + '" loading="lazy">'
        : '<span class="logo-name">' + esc(it.name) + '</span>';
      return '<' + tag + ' class="logo-tile"' + href + '>' + inner +
        (it.detail ? '<small>' + esc(it.detail) + '</small>' : '') +
        (it.body ? '<p>' + fmt(it.body) + '</p>' : '') + '</' + tag + '>';
    }
  };
  var WRAP = { lineup: 'rows', news: 'posts', vendors: 'cards c3', sponsors: 'logo-grid', partners: 'logo-grid' };

  function applyLists(lists) {
    lists = lists || {};
    document.querySelectorAll('[data-list]').forEach(function (host) {
      var name = host.getAttribute('data-list');
      var filter = host.getAttribute('data-filter');
      var items = (lists[name] || []).filter(function (it) {
        return it && it.name && (!filter || it.category === filter);
      });
      if (!items.length) return;
      var r = RENDER[name] || RENDER.logos;
      host.className = WRAP[name] || '';
      host.innerHTML = items.map(r).join('');
      var emptyId = host.getAttribute('data-empty');
      if (emptyId) {
        var empty = document.getElementById(emptyId);
        if (empty) empty.style.display = 'none';
      }
    });
    document.querySelectorAll('[data-show-list]').forEach(function (sec) {
      var n = (lists[sec.getAttribute('data-show-list')] || []).filter(function (i) { return i && i.name; }).length;
      if (n) sec.hidden = false;
    });
  }

  function apply(d) {
    if (!d) return;
    applyText(d.text);
    applyImages(d.images);
    applyLinks(d.links);
    applyLists(d.lists);
    document.dispatchEvent(new CustomEvent('ascf:content'));
  }

  window.ASCF_CONTENT = { load: load, apply: apply, fmt: fmt };

  function go() { load().then(apply); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go);
  else go();
})();
