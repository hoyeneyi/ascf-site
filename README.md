# America's Spring Canvas Festival — Preview Build

Static multi-page site. No build step, no dependencies, no server code.

## Deploy to GitHub Pages

```bash
git init
git add .
git commit -m "ASCF preview build"
git branch -M main
git remote add origin https://github.com/<you>/ascf-site.git
git push -u origin main
```

Then: **Settings → Pages → Source: Deploy from a branch → main / (root)**

Live at `https://<you>.github.io/ascf-site/` in about a minute.

## Pages

| File | Purpose |
|---|---|
| `index.html` | Home — rotating banner, location, section tiles |
| `about.html` | The Festival — what it is, the three days, venue |
| `lineup.html` | Stages and lineup, with announcement signup |
| `rps.html` | RPS World Championship — format, prizes, registration |
| `vendors.html` | Booth tiers and vendor application form |
| `sponsors.html` | Sponsorship packages and deck request |
| `tickets.html` | Pass tiers and presale signup |
| `contact.html` | General contact form |

Shared assets live in `assets/` — one stylesheet, one script, all placeholder art.
Editing the nav or footer means editing all eight files. `build.py` + `pages.py`
regenerate them all from one template if you'd rather change it in one place.

## Two settings to change before launch

Both live at the top of `assets/site.js`:

```js
var ACCESS_CODE = 'canvas2028';   // change before sending the preview link
var GA_ID = 'G-XXXXXXXXXX';       // real GA4 ID at launch
```

The GA4 measurement ID also appears in the `<head>` of each page. Find and replace
`G-XXXXXXXXXX` across all eight files.

## Analytics

Two layers:

1. **Google Analytics 4** — standard pageview tracking. Because each section is a
   real page with its own URL, GA reports traffic, time on page, and drop-off
   per section. A single-page site cannot do this.
2. **Click tracking** — every button and link carries a `data-track` attribute and
   fires a GA4 `ascf_click` event. To track something new, add the attribute:
   ```html
   <a href="..." data-track="my_button_name">Click me</a>
   ```

The **Click data** button (bottom right) opens a live panel showing what's been
clicked. Counts are stored locally in the browser so the tracking can be
demonstrated before GA is connected. Remove the button and panel from the
footer block before going public.

## Access gate

The site is gated by a code and carries `robots.txt` plus a `noindex` tag, so it
stays out of search results.

**This is a soft gate, not security.** Page source is downloadable by anyone with
the URL. It keeps casual visitors and crawlers out, which is all a draft needs.
Before anything sensitive goes up — sponsor pricing, financials, contact data —
move to Cloudflare Access on the custom domain. That's real authentication and
takes about twenty minutes.

## Forms

All forms are front-end only. They validate and show a confirmation, but nothing
is sent or stored. Wiring them up needs either:

- **Formspree / Netlify Forms** — fastest, no backend, emails you each submission
- **A real backend** — required if vendor and sponsor applications need to be
  searchable, assignable, or exportable

Email capture needs a mailing list provider connected (Mailchimp, ConvertKit,
or similar) before launch, or signups are lost.

## Placeholder content

Everything marked `TBD` needs client input. The placeholder artwork in
`assets/img/` is generated SVG — swap for real photography as it comes in.
Sizes: hero images 1600×900, tiles 800×600.

Charity partner logos are **not** on the site. They should not go up until
written permission is on file from each organization.

## Still to build

1. Real content in place of TBD markers
2. Forms wired to a real destination
3. Mailing list provider connected
4. Admin panel with a backend so the client edits content without a developer
5. Ticketing and registration platform (Phase 2)
6. Custom domain, real GA4 property, Cloudflare Access
