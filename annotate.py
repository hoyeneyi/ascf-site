"""
Makes a built page editable.

Walks the HTML, finds every piece of client-facing text, every image and every
email/social link, and tags it:

    data-edit="key"   text the client can rewrite
    data-img="key"    a background image the client can replace
    data-link="key"   a link destination the client can change

It also returns schema entries (key, type, label, section, default) that the
admin portal uses to draw its forms, in the same order they appear on the page.
Keys are derived from the default text, so they stay stable across rebuilds.
"""
import hashlib
import html as htmllib
import os
import re
from html.parser import HTMLParser

TEXT_TAGS = {"h1", "h2", "h3", "p", "small", "b", "span", "li", "summary", "div", "a", "button"}
INLINE_OK = {"b", "br"}                      # plus span.tbd, handled below
CONTAINERS = {"section", "footer"}
CONTAINER_CLASSES = {"slide", "pagehead", "band", "identity", "ticker", "countdown", "topbar"}
GLOBAL_CLASSES = {"topbar"}                   # plus <footer>
SKIP_CLASSES = {"navlinks", "mobilemenu", "cd", "dots", "sr", "credit", "totop", "wm", "bar", "glow", "scrim",
                # The Coming Soon page is driven by Site status settings,
                # not by the page editor, so it must not become fields.
                "cs-root"}
SKIP_TAGS = {"nav", "head", "script", "style"}
# Labels that count as "a heading" when naming a nearby image.
HEADING_LABELS = {"Page title", "Heading", "Subheading", "Banner headline",
                  "Section heading", "Card title", "Tier name"}
KIND_LABEL = {
    "h1": "Page title", "h2": "Heading", "h3": "Subheading", "p": "Paragraph",
    "small": "Small text", "b": "Bold text", "li": "List item", "summary": "Expandable title",
    "a": "Button / link text", "button": "Button text", "span": "Label", "div": "Label",
}


def _h(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:8]


def _plain(inner):
    """HTML fragment -> editable plain text. **bold**, newlines for <br>."""
    s = re.sub(r"\s+", " ", inner)
    s = re.sub(r"\s*<br\s*/?>\s*", "\n", s, flags=re.I)
    s = re.sub(r"<b>(.*?)</b>", r"**\1**", s, flags=re.S | re.I)
    s = re.sub(r'<span class="tbd">(.*?)</span>', r"\1", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = htmllib.unescape(s)
    lines = [re.sub(r"[ \t\r\f\v]+", " ", ln).strip() for ln in s.split("\n")]
    return "\n".join(lines).strip()


class _Walker(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.line_starts = [0]
        for m in re.finditer(r"\n", src):
            self.line_starts.append(m.end())
        self.stack = []
        self.text_cands = []
        self.img_cands = []
        self.link_cands = []
        self.containers = {}
        self._cid = 0
        self._card = 0

    def _abs(self):
        ln, col = self.getpos()
        return self.line_starts[ln - 1] + col

    def _flags(self):
        skip = any(e["skip"] for e in self.stack)
        glob = any(e["global"] for e in self.stack)
        cont = next((e["cid"] for e in reversed(self.stack) if e["cid"] is not None), None)
        return skip, glob, cont

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        start = self._abs()
        tag_end = self.src.index(">", start)
        parent_skip, parent_glob, parent_cont = self._flags()

        is_container = tag in CONTAINERS or bool(classes & CONTAINER_CLASSES)
        cid = None
        if is_container:
            self._cid += 1
            cid = self._cid
            kind = next(iter(classes & CONTAINER_CLASSES), tag)
            self.containers[cid] = {"kind": kind, "heading": None}

        skip_here = parent_skip or tag in SKIP_TAGS or bool(classes & SKIP_CLASSES) \
            or a.get("aria-hidden") == "true" and tag != "div" or "data-u" in a
        glob_here = parent_glob or tag == "footer" or bool(classes & GLOBAL_CLASSES)

        # background images
        style = a.get("style") or ""
        m = re.search(r"url\('([^']+)'\)", style)
        if m and not skip_here:
            self.img_cands.append({"pos": tag_end, "url": m.group(1), "classes": classes,
                                   "global": glob_here, "cont": cid or parent_cont})

        if tag in ("br",):
            if self.stack:
                pass
            return

        # footer internal nav links are structure, not content
        if tag == "a" and glob_here and not (a.get("href", "").startswith("mailto:") or a.get("href") == "#"):
            skip_here = True
        if tag == "h4" and glob_here:
            skip_here = True

        anc = set()
        for e in self.stack:
            anc |= e["classes"]
        card = next((e["card"] for e in reversed(self.stack) if e["card"]), None)
        if "card" in classes:
            self._card += 1
            card = self._card

        self.stack.append({
            "tag": tag, "classes": classes, "attrs": a, "start": start, "tag_end": tag_end,
            "skip": skip_here, "global": glob_here, "cid": cid,
            "cont": cid or parent_cont, "bad_child": False,
            "anc": anc, "card": card,
        })
        if len(self.stack) > 1:
            parent = self.stack[-2]
            ok_inline = tag in INLINE_OK or (tag == "span" and "tbd" in classes)
            if not ok_inline:
                parent["bad_child"] = True

    def handle_startendtag(self, tag, attrs):
        if tag == "br":
            return
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack:
            return
        # tolerate stray/misnested tags by popping to the matching one
        idx = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                idx = i
                break
        if idx is None:
            return
        while len(self.stack) > idx + 1:
            self.stack.pop()
        el = self.stack.pop()
        end = self._abs()
        inner = self.src[el["tag_end"] + 1:end]
        text = _plain(inner)

        # remember the first heading of each container, for admin grouping
        if el["tag"] in ("h1", "h2") and el["cont"] and text:
            c = self.containers.get(el["cont"])
            if c and not c["heading"]:
                c["heading"] = text.replace("\n", " ")

        if el["skip"]:
            return
        a = el["attrs"]
        if el["tag"] == "a":
            href = a.get("href", "")
            if href.startswith("mailto:") or href == "#":
                self.link_cands.append({"pos": el["tag_end"], "text": text, "href": href,
                                        "global": el["global"], "cont": el["cont"]})
        if el["tag"] in TEXT_TAGS and not el["bad_child"] and text and re.search(r"[A-Za-z0-9]", text):
            self.text_cands.append({"start": el["start"], "end": end, "pos": el["tag_end"],
                                    "tag": el["tag"], "classes": el["classes"], "text": text,
                                    "global": el["global"], "cont": el["cont"],
                                    "anc": el["anc"], "card": el["card"]})


def _label_for(c, cont_kind, section, is_tier):
    """Name a field by where it sits, not just by its tag.

    Falls through to KIND_LABEL when nothing more specific applies, so a
    layout this doesn't know about still gets a usable label.
    """
    tag, cls, anc, text = c["tag"], c["classes"], c["anc"], c["text"]

    # explicit class hints win outright
    if "kicker" in cls:
        return "Small caps label"
    if "tag" in cls:
        return "Banner tag"

    # homepage banner slides
    if cont_kind == "slide":
        if tag in ("h1", "h2"):
            return "Banner headline"
        if tag == "p":
            return "Banner text"
        if tag in ("a", "button"):
            return "Banner button"

    # the Pontiac roll call
    if "history" in anc:
        if tag == "b":
            return "Year"
        if tag == "span":
            return "Event name"
    if tag == "b" and re.fullmatch(r"\d{4}", text):
        return "Year"

    # sponsorship tiers are cards carrying a price
    if is_tier:
        if tag == "h3":
            return "Tier name"
        if tag == "li":
            return "Tier benefit"
        if tag == "div" and text.lstrip().startswith("$"):
            return "Tier price"

    # feature cards
    if "card" in anc:
        if tag == "h3":
            return "Card title"
        if tag == "p":
            return "Card text"
        if "more" in cls or tag in ("a", "button"):
            return "Card link text"

    # stat tiles: a big number over a caption
    if "stat" in anc or "items" in anc:
        if tag == "span":
            return "Stat number"
        if tag == "small":
            return "Stat label"

    # section headers
    if "section-head" in anc:
        if tag in ("h1", "h2"):
            return "Section heading"
        if tag == "p":
            return "Section intro"
    if "lede" in cls:
        return "Section intro"

    if section == "Footer":
        return "Footer text"

    return KIND_LABEL.get(tag, "Text")


def annotate(src, page_id):
    w = _Walker(src)
    w.feed(src)

    # outermost text-only element wins; drop anything nested inside another candidate
    cands = sorted(w.text_cands, key=lambda c: (c["start"], -c["end"]))
    kept, last_end = [], -1
    for c in cands:
        if c["start"] < last_end:
            continue
        kept.append(c)
        last_end = c["end"]

    inserts, fields = [], []

    def section_of(c):
        cont = w.containers.get(c["cont"]) if c["cont"] else None
        if c["global"]:
            return "Top banner" if cont and cont["kind"] == "topbar" else "Footer"
        if not cont:
            return "Page"
        fixed = {"identity": "Festival name block", "pagehead": "Page header",
                 "ticker": "Scrolling ticker", "countdown": "Countdown"}
        if cont["kind"] in fixed:
            return fixed[cont["kind"]]
        if cont["heading"]:
            return cont["heading"]
        return {"ticker": "Scrolling ticker", "countdown": "Countdown",
                "identity": "Festival name block"}.get(cont["kind"], "Section")

    # a card holding a price is a sponsorship tier
    tier_cards = {c["card"] for c in kept
                  if c["card"] and c["tag"] == "div" and c["text"].lstrip().startswith("$")}

    for c in kept:
        scope = "global" if c["global"] else page_id
        key = f"{scope}__{c['tag']}__{_h(c['text'])}"
        inserts.append((c["pos"], f' data-edit="{key}"'))
        cont = w.containers.get(c["cont"]) if c["cont"] else None
        kind = _label_for(c, cont["kind"] if cont else None, section_of(c),
                          c["card"] in tier_cards)
        long = c["tag"] == "p" or len(c["text"]) > 90 or "\n" in c["text"]
        fields.append({"key": key, "type": "long" if long else "text", "label": kind,
                       "section": section_of(c), "default": c["text"], "pos": c["start"],
                       "global": c["global"]})

    counters = {}
    for im in w.img_cands:
        scope = "global" if im["global"] else page_id
        base = os.path.splitext(os.path.basename(im["url"]))[0]
        n = counters.get(base, 0) + 1
        counters[base] = n
        key = f"{scope}__img__{re.sub(r'[^a-z0-9]+', '_', base.lower())}_{n}"
        inserts.append((im["pos"], f' data-img="{key}"'))
        # label from the next heading after the image
        nxt = next((f for f in fields if f["pos"] > im["pos"] and f["label"] in HEADING_LABELS), None)
        what = "Banner image" if "bg" in im["classes"] else "Image"
        label = f"{what} — {nxt['default'][:48]}" if nxt else what
        fields.append({"key": key, "type": "image", "label": label,
                       "section": section_of({"cont": im["cont"], "global": im["global"]}),
                       "default": im["url"], "pos": im["pos"], "global": im["global"]})

    seen = {}
    for ln in w.link_cands:
        scope = "global" if ln["global"] else page_id
        base = f"{ln['text']}"
        n = seen.get(base, 0) + 1
        seen[base] = n
        key = f"{scope}__link__{_h(base + str(n))}"
        inserts.append((ln["pos"], f' data-link="{key}"'))
        what = "Email / link for" if ln["href"].startswith("mailto:") else "Link for"
        fields.append({"key": key, "type": "link", "label": f"{what} “{ln['text'].replace(chr(10), ' ')[:40]}”",
                       "section": section_of({"cont": ln["cont"], "global": ln["global"]}),
                       "default": "" if ln["href"] in ("#", "mailto:") else ln["href"],
                       "pos": ln["pos"], "global": ln["global"]})

    # apply inserts back to front so earlier offsets stay valid
    out = src
    for pos, attr in sorted(inserts, key=lambda x: x[0], reverse=True):
        out = out[:pos] + attr + out[pos:]

    fields.sort(key=lambda f: f["pos"])
    return out, fields
