# America's Spring Canvas Festival — Website

Static multi-page site. No build step required to deploy — everything in this folder is ready to push.

## Deploy to GitHub Pages

```bash
git init
git add .
git commit -m "ASCF site"
git branch -M main
git remote add origin https://github.com/<you>/ascf-site.git
git push -u origin main
```

Settings → Pages → Deploy from a branch → `main` / root.

## Pages

| URL | What's there |
|---|---|
| `/` | Rotating hero banner, stats, the three e's, mission, tournament, signup |
| `/mission/` | The conflict resolution campaign, banquet, charity partners |
| `/eateries/` | eATERIES — 50 restaurants and food trucks |
| `/exhibits/` | eXHIBITS — 150 artists |
| `/entertainment/` | eNTERTAINMENT — stages and lineup |
| `/tournament/` | RPS tournament |
| `/attractions/` | Rides, games, Kids Zone, fireworks |
| `/involved/` | Sponsorship tiers, vendor/artist/volunteer/press |
| `/admin/` | Admin portal (demo login: `admin` / `canvas2028`) |

## Analytics

Open `assets/js/analytics.js` and replace `G-XXXXXXXXXX` with the Measurement ID from
analytics.google.com. Nothing is sent until that's done.

Click tracking is already wired. Every button and nav link carries a `data-track` attribute,
so the reports show which CTAs get used, which hero slide converts, which sponsorship tier
gets opened most, and how far down each page people scroll.

## Email capture

Three places: the bar at the top of every page, the homepage signup section, and an
inline form on each "announced soon" section.

Set `FORM_ENDPOINT` near the top of `assets/js/site.js` to a Formspree endpoint to start
collecting. Until then submissions confirm on screen but aren't stored.

## Admin portal

`/admin/` is a working demo — add lineup artists, vendors and sponsors, edit the homepage
location line and the top banner. Published items appear on the live pages.

**It stores to the browser only.** Production needs Firebase Auth for login and Firestore
for content. The swap is contained: in `assets/js/site.js`, `loadContent()` and `loadLineup()`
become Firestore reads; in `admin/index.html`, `read()` and `write()` become Firestore calls.
Everything else stays.

## Images

All images in `assets/img/` are generated SVG placeholders, clearly labelled. Drop in real
photography with the same filenames and the site picks it up with no code changes.

## Search engines

`robots.txt` disallows everything and each page carries a `noindex` tag. Delete both when
the site is ready to be public.

## Rebuilding

Pages are generated from `build.py` in the parent folder so the header, nav and footer stay
in sync. Edit `build.py`, run `python3 build.py`, and the `site/` folder is rewritten.
