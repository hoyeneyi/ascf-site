# America's Spring Canvas Festival — Website

Static, mobile-first, no build step needed to deploy. Push this folder as the repo root.

## Pages

| URL | What's there |
|---|---|
| `/` | Identity, 6-slide rotating banner, community mission box, experience cards, signup |
| `/mission/` | The mission and the awards banquet |
| `/campaign/` | Conflict Resolution Campaign — problem, change, meaning, plan |
| `/eateries/` | Food |
| `/exhibits/` | Arts & Culture |
| `/entertainment/` | Entertainment — stages and lineup |
| `/tournament/` | Competition — RPS tournament |
| `/attractions/` | Attractions |
| `/involved/` | Founding partner, why partner with us, start the conversation |
| `/involved/sponsorship/` | Who attends, brand exposure, community impact, tier levels, request info |
| `/involved/partners/` | Community partners (distinct from sponsors) |
| `/news/` | News & updates |
| `/contact/` | Eight categorized inquiry routes |
| `/admin/` | Admin portal — demo login `admin` / `canvas2028` |

## Still needed from the client

- Domain (they asked about ascf.com — check availability and price first)
- Logo — none exists yet; the site runs on type only, and the logo competition is a banner slide
- Real photography — all images are generated placeholders
- Email address to receive signups
- Contact addresses for the eight inquiry categories
- Social media handles for the footer links

## Analytics

Replace `G-XXXXXXXXXX` in `assets/js/analytics.js` with the GA4 Measurement ID.
Tracking already covers: page views, email signups by location, sponsorship and partner
clicks, which hero slide converts, vendor/exhibitor/volunteer clicks, nav use, social
clicks, and scroll depth.

## Email capture

Set `FORM_ENDPOINT` in `assets/js/site.js`. Signup appears in the top bar of every page
and as a full section on nine pages.

## Admin portal

Tabs: General, Lineup, News, Vendors & Artists, Sponsors, Analytics. Demo storage is the
browser only. Production swaps `read()`/`write()` in `admin/index.html` and
`loadContent()`/`loadLineup()` in `assets/js/site.js` for Firestore, plus Firebase Auth
for login.

## Ownership

Accounts should be created in the client's name — domain, hosting, analytics, forms,
email list. They own the asset; we manage it.

## Rebuilding

`python3 build.py` regenerates `site/` from the shared template.
`python3 make_placeholders.py` regenerates the placeholder images.
