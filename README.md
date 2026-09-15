# America's Spring Canvas Festival — Preview Site

Phase 1 preview build. Static, single page, no dependencies.

## Deploy to GitHub Pages

```bash
git init
git add .
git commit -m "ASCF preview build"
git branch -M main
git remote add origin https://github.com/<you>/ascf-site.git
git push -u origin main
```

Then in the repo: **Settings → Pages → Source: Deploy from a branch → main / (root)**.

Live at `https://<you>.github.io/ascf-site/` in about a minute.

## Access code

Set in `index.html`, near the bottom:

```js
var ACCESS_CODE='canvas2028';
```

Change it before sending the link. The code unlocks the page for the rest of the browser session.

**This is a soft gate, not security.** The page source is still downloadable by anyone who finds the URL. It keeps casual visitors and search engines out, which is all it needs to do while the site is a draft. Before anything sensitive goes up — sponsor pricing, financials, contact data — move to Cloudflare Access on the custom domain. That's real authentication and takes about twenty minutes to set up.

`robots.txt` disallows all crawlers and the page carries a `noindex` meta tag, so it won't surface in search.

## Admin preview

The button at bottom right opens a mock lineup editor. Add an artist, publish, and it appears in the lineup section. It's a demo only — nothing persists on refresh. The real version needs a backend.

## What's placeholder

- All lineup slots
- Venue confirmation
- RPS registration dates, rules, eligibility
- Contact addresses
- Charity partners (pending permission to display logos)
- Photography — currently none; the design uses type and color instead of stock images

## Next

1. Client fills in the content questionnaire
2. Swap placeholders for real content
3. Wire the email capture and sponsor inquiry forms
4. Build the admin panel with a real backend
5. Point the custom domain, move the gate to Cloudflare Access
