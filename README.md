# America's Spring Canvas Festival — Website

Static site on GitHub Pages. Content is edited by the client through `/admin/`,
stored in Firebase, and read by the public pages at load time. No rebuild or
redeploy is needed for content changes.

---

## Go-live checklist (developer, one time, ~30 minutes)

Do these in the **client's** Google account so they own the project. Add
yourself as an Owner under Project settings → Users and permissions.

### 1. Create the Firebase project
1. console.firebase.google.com → **Add project** → name it (e.g. `ascf-website`). Analytics optional.
2. **Upgrade to Blaze** (bottom-left plan badge). Required for image uploads — Firebase
   no longer offers Storage on the free Spark plan. No-cost usage still applies; at this
   site's scale the bill should be $0.
3. In Google Cloud → Billing → **Budgets & alerts**, set a $5 monthly budget with email alerts
   to the client and you. This is the guardrail against surprises.

### 2. Turn on the three services
- **Authentication** → Get started → **Email/Password** → Enable.
  Then **Users** → Add user for each editor (client email + temporary password).
- **Firestore Database** → Create database → Production mode → a US region.
- **Storage** → Get started → Production mode → same region.

### 3. Paste in the security rules
- Open `firestore.rules` and `storage.rules` from this folder.
- Replace the two placeholder emails in **both** files with the real editor emails.
- Firestore → **Rules** tab → paste → Publish. Storage → **Rules** tab → paste → Publish.

The allowlist matters: Firebase lets anyone create an account with the public
config, so "signed in" alone is not enough. Only listed emails can write.

### 4. Connect the site
1. Project settings → **Your apps** → Web (`</>`) → register → copy the `firebaseConfig` object.
2. Paste it into `assets/js/firebase-config.js`, replacing `null`.
3. Commit and push. The yellow "Demo mode" banner disappears from `/admin/`.

These config values are designed to be public. Security comes from the rules.

### 5. Hand off
- Send the client the `/admin/` link and their temporary password.
- Have them sign in once and use **Forgot your password?** to set their own.
- Send the Admin Guide.

---

## Also still to configure

| What | Where |
|---|---|
| Google Analytics | Replace `G-XXXXXXXXXX` in `assets/js/analytics.js` |
| Email signups | Set `FORM_ENDPOINT` in `assets/js/site.js` (Formspree, or a Mailchimp/Brevo form URL) |
| Custom domain | GitHub → Settings → Pages → Custom domain. Then set `SITE_URL` and `REPO_BASE = "/"` in `build.py`, rebuild, push |
| Go public | Delete `robots.txt` and remove the `noindex` meta tag in `build.py`, rebuild, push |

---

## How editing works

`build.py` generates every page, then `annotate.py` walks the output and tags
every piece of client-facing text (`data-edit`), every image (`data-img`), and
every email/social/document link (`data-link`). It writes
`assets/js/schema.js`, which the admin uses to draw its forms — grouped by page
and section, in page order. Currently **468 editable items across 14 groups**.

Keys come from the original text, so they are stable across rebuilds. If you
change default copy in `build.py`, any client override of that exact item is
orphaned and the new default shows — expected behaviour.

`assets/js/content.js` fetches one Firestore document (`site/content`) over
REST — no Firebase SDK on public pages — caches it for 60 seconds per tab, and
applies text, images, links and the five lists (lineup, news, vendors,
sponsors, partners).

Without a Firebase config everything runs in **demo mode**: admin login is
`admin` / `canvas2028` and edits save to that one browser.

## Rebuilding

    python3 build.py              # regenerate site/ and schema.js
    python3 make_placeholders.py  # regenerate placeholder images
    python3 make_brand_assets.py  # regenerate share image, favicon, touch icon

## Files

    index.html, */index.html   public pages
    admin/index.html           editor portal
    404.html                   branded not-found page
    assets/css/site.css        all styling
    assets/js/content.js       applies published content
    assets/js/site.js          nav, carousel, analytics events, signup, motion
    assets/js/schema.js        generated list of editable items
    assets/js/firebase-config.js
    firestore.rules, storage.rules
