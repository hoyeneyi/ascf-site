#!/usr/bin/env python3
"""Builds the ASCF static site. Run: python3 build.py"""
import os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")

# nav: (href, label, [children]) — href None means the parent only opens the group
NAV = [
    ("", "Home", []),
    ("mission/", "Mission", [("campaign/", "Conflict Resolution Campaign")]),
    (None, "Experience", [
        ("eateries/", "Food — eATERIES"),
        ("exhibits/", "Arts &amp; Culture — eXHIBITS"),
        ("entertainment/", "Entertainment — eNTERTAINMENT"),
        ("tournament/", "Competition — RPS Tournament"),
        ("attractions/", "Attractions"),
    ]),
    ("involved/", "Get Involved", [
        ("involved/sponsorship/", "Sponsorship"),
        ("involved/partners/", "Community Partners"),
    ]),
    ("news/", "News", []),
    ("contact/", "Contact", []),
]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700'
         '&family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">')

SIGNUP_COPY = ("Be the first to receive festival announcements, partnership "
               "opportunities, community initiatives and event updates.")
SIGNUP_BTN = "JOIN THE CANVAS COMMUNITY"

# Where the site lives. Change both when the custom domain goes live.
SITE_URL = "https://ascfestival.com/"
REPO_BASE = "/"                    # used only by the 404 page


def link(base, href):
    # The homepage is linked as a folder ("./", "../"), never as index.html.
    # Analytics counts "/" and "/index.html" as two different pages otherwise.
    return (base or "./") if href == "" else f"{base}{href}"


def nav_html(base, current):
    desk, mob = [], []
    for href, label, kids in NAV:
        in_group = current == href or any(current == k for k, _ in kids)
        if kids:
            cls = ' class="has-sub current"' if in_group else ' class="has-sub"'
            subs = ""
            if href is not None:
                subs += (f'<a href="{link(base, href)}" data-track="nav_click" '
                         f'data-label="{label} overview">{label} overview</a>')
            subs += "".join(
                f'<a href="{link(base, k)}" data-track="nav_click" data-label="{kl}">{kl}</a>'
                for k, kl in kids)
            desk.append(f'<div{cls}><button type="button">{label}</button>'
                        f'<div class="sub">{subs}</div></div>')

            mob.append(f'<span class="subhead">{label}</span>')
            if href is not None:
                mob.append(f'<a class="child" href="{link(base, href)}" '
                           f'data-track="nav_click_mobile" data-label="{label} overview">{label} overview</a>')
            for k, kl in kids:
                a = " active" if current == k else ""
                mob.append(f'<a class="child{a}" href="{link(base, k)}" '
                           f'data-track="nav_click_mobile" data-label="{kl}">{kl}</a>')
        else:
            cls = ' class="active"' if current == href else ""
            desk.append(f'<a href="{link(base, href)}"{cls} data-track="nav_click" data-label="{label}">{label}</a>')
            mob.append(f'<a href="{link(base, href)}"{cls} data-track="nav_click_mobile" data-label="{label}">{label}</a>')
    return "\n        ".join(desk), "\n      ".join(mob)


def page(slug, title, description, body, base, current="", path=None):
    desk, mob = nav_html(base, current)
    url = SITE_URL + (path if path is not None else current)
    home_href = base or "./"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#070C0D">
<script>document.documentElement.classList.add('js')</script>
<link rel="icon" type="image/svg+xml" href="{base}assets/img/favicon.svg">
<link rel="apple-touch-icon" href="{base}assets/img/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="America's Spring Canvas Festival">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{SITE_URL}assets/img/og.png">
{FONTS}
<link rel="stylesheet" href="{base}assets/css/site.css">
<script src="{base}assets/js/analytics.js"></script>
</head>
<body data-page="{slug}">

<div class="topbar">
  <div class="wrap">
    <p>Festival news, straight to your inbox</p>
    <form data-signup="topbar">
      <label class="sr" for="tb-{slug}">Email address</label>
      <input id="tb-{slug}" type="email" placeholder="your@email.com" required>
      <button type="submit" data-track="cta_click" data-label="topbar_signup">{SIGNUP_BTN}</button>
    </form>
    <span class="ok" style="display:none"></span>
  </div>
</div>

<nav class="nav">
  <div class="wrap">
    <a class="brand" href="{home_href}" data-track="nav_click" data-label="brand_home">
      AMERICA'S SPRING CANVAS FESTIVAL
      <span>PONTIAC, MICHIGAN · MEMORIAL DAY WEEKEND 2028</span>
    </a>
    <div class="navlinks">
        {desk}
    </div>
    <button class="navtoggle" aria-label="Menu" aria-expanded="false" aria-controls="mobilemenu"><i></i><i></i><i></i></button>
  </div>
</nav>
<!-- Lives outside <nav> on purpose: the header's backdrop-filter would otherwise
     become the containing block for this fixed panel and collapse it. -->
<div class="mobilemenu" id="mobilemenu">
      {mob}
</div>

{body}

<footer>
  <div class="wrap">
    <div class="footgrid">
      <div>
        <div class="fbrand gradient-text">AMERICA'S<br>SPRING CANVAS FESTIVAL</div>
        <div class="meta">
          Pontiac, Michigan 48341<br>
          May 26&ndash;29, 2028 &middot; Memorial Day Weekend
        </div>
        <div class="social">
          <a href="#" data-track="social_click" data-label="instagram">INSTAGRAM</a>
          <a href="#" data-track="social_click" data-label="facebook">FACEBOOK</a>
          <a href="#" data-track="social_click" data-label="tiktok">TIKTOK</a>
          <a href="#" data-track="social_click" data-label="youtube">YOUTUBE</a>
          <a href="#" data-track="social_click" data-label="linkedin">LINKEDIN</a>
        </div>
      </div>
      <div>
        <h4>THE FESTIVAL</h4>
        <a href="{base}mission/">Mission</a>
        <a href="{base}campaign/">Conflict Resolution Campaign</a>
        <a href="{base}eateries/">Food</a>
        <a href="{base}exhibits/">Arts &amp; Culture</a>
        <a href="{base}entertainment/">Entertainment</a>
        <a href="{base}tournament/">RPS Tournament</a>
        <a href="{base}attractions/">Attractions</a>
      </div>
      <div>
        <h4>TAKE PART</h4>
        <a href="{base}involved/">Get Involved</a>
        <a href="{base}involved/sponsorship/">Sponsorship</a>
        <a href="{base}involved/partners/">Community Partners</a>
        <a href="{base}news/">News &amp; Updates</a>
        <a href="{base}contact/">Contact</a>
      </div>
    </div>
    <div class="footbase">
      <span>&copy; America's Spring Canvas Festival &middot; Pontiac, Michigan</span>
      <button class="totop" type="button">BACK TO TOP &uarr;</button>
    </div>
  </div>
  <div class="footbar"></div>
</footer>

<script src="{base}assets/js/firebase-config.js"></script>
<script src="{base}assets/js/content.js"></script>
<script src="{base}assets/js/site.js"></script>
</body>
</html>
"""


def band(base, heading, text, btn_label, btn_href, track):
    return f"""
<div class="band">
  <div class="wrap">
    <h2>{heading}</h2>
    <p>{text}</p>
    <a class="btn btn-solid" href="{link(base, btn_href)}" data-track="cta_click" data-label="{track}">{btn_label}</a>
  </div>
</div>"""


def pagehead(kicker, h1, lede, wm=None):
    mark = wm if wm is not None else kicker
    return f"""
<div class="pagehead">
  <div class="glow"></div>
  <div class="wm" aria-hidden="true">{mark}</div>
  <div class="wrap">
    <div class="kicker">{kicker}</div>
    <h1 class="gradient-text">{h1}</h1>
    <div class="ribbon"></div>
    <p class="lede">{lede}</p>
  </div>
</div>"""


def signup_section(base, where, heading="Join the Canvas community."):
    return f"""
<section id="notify">
  <div class="wrap" style="text-align:center">
    <div class="kicker">Email signup</div>
    <h2>{heading}</h2>
    <p class="lede" style="margin:14px auto 24px">{SIGNUP_COPY}</p>
    <form class="signup" data-signup="{where}">
      <label class="sr" for="em-{where}">Email address</label>
      <input id="em-{where}" type="email" placeholder="your@email.com" required>
      <button class="btn btn-solid" type="submit" data-track="cta_click" data-label="{where}_signup">{SIGNUP_BTN}</button>
    </form>
    <div class="signup-note"></div>
  </div>
</section>"""


# ============================== HOME ==============================
HISTORY = """<ul class="history">
          <li><b>1982</b><span>Super Bowl XVI</span></li>
          <li><b>1987</b><span>WrestleMania III</span></li>
          <li><b>1987</b><span>Papal Mass</span></li>
          <li><b>1994</b><span>FIFA World Cup</span></li>
          <li class="next"><b>2028</b><span>America's Spring Canvas Festival</span></li>
        </ul>"""
_TICK_WORDS = ["FOOD", "ART", "MUSIC", "COMPETITION", "COMMUNITY", "CONFLICT RESOLUTION", "PONTIAC 2028"]
TICKER = "".join(f'<span>{w}</span><span class="dot"></span>' for w in _TICK_WORDS)
SLIDES = [
    ("hero-pontiac", "PONTIAC, MICHIGAN",
     "The world has come<br>to Pontiac before.",
     HISTORY,
     [("campaign/", "Join the movement", "btn-solid", "hero_join"),
      ("involved/", "Become a sponsor", "btn-ghost", "hero_sponsor")]),
    ("hero-art", "FOUR DAYS &middot; EIGHT STAGES",
     "Come for the<br>music.",
     "National headliners at night, local artists all afternoon, and eight stages running from noon until the fireworks.",
     [("entertainment/", "See the lineup", "btn-solid", "hero_lineup"),
      ("./#notify", "Get festival updates", "btn-ghost", "hero_updates")]),
    ("hero-food", "50 RESTAURANTS &amp; FOOD TRUCKS",
     "Stay for the<br>food.",
     "Fifty local kitchens serving the cooking of the communities that built this country &mdash; all in one place, for four days only.",
     [("eateries/", "Explore the food", "btn-solid", "hero_eateries"),
      ("involved/", "Vendor interest form", "btn-ghost", "hero_vend")]),
    ("hero-rps", "150 ARTISTS &amp; EXHIBITORS",
     "Take a piece<br>of it home.",
     "Painting, glasswork, jewelry and print from a hundred and fifty makers, showing and selling across the whole weekend.",
     [("exhibits/", "Explore arts &amp; culture", "btn-solid", "hero_exhibits"),
      ("involved/", "Exhibitor application", "btn-ghost", "hero_exhibit_apply")]),
    ("hero-crowd", "50,000 CONTESTANTS &middot; 4 &times; $25,000",
     "Settle it the<br>old way.",
     "The largest Rock Paper Scissors tournament ever staged, with referees, announcers and four grand prizes of twenty-five thousand dollars.",
     [("tournament/", "Tournament details", "btn-solid", "hero_rps"),
      ("./#notify", "Get registration alerts", "btn-ghost", "hero_rps_alert")]),
    ("hero-art", "OPEN CALL",
     "Don't notice<br>a logo? Exactly.",
     "We haven't designed one yet, because we'd rather the community did. The Spring Canvas logo "
     "competition opens soon, and the winning mark becomes the face of the festival.",
     [("./#notify", "Get competition details", "btn-solid", "hero_logo_comp"),
      ("campaign/", "Why we're doing this", "btn-ghost", "hero_logo_why")]),
]


def home():
    base = ""
    slides = []
    for n, (img, tag, h, p, ctas) in enumerate(SLIDES):
        buttons = "".join(
            f'<a class="btn {c}" href="{link(base, href)}" data-track="cta_click" data-label="{t}">{label}</a>'
            for href, label, c, t in ctas)
        body_html = p if p.lstrip().startswith("<") else f"<p>{p}</p>"
        mod = " slide-pop" if img == "hero-pontiac" else ""
        slides.append(f"""
    <div class="slide{mod}{' on' if n == 0 else ''}">
      <div class="bg" style="background-image:url('{base}assets/img/{img}.svg')"></div>
      <div class="scrim"></div>
      <div class="inner wrap">
        <div class="copy">
        <span class="tag">{tag}</span>
        <h2 class="gradient-text">{h}</h2>
        {body_html}
        <div class="cta-row">{buttons}</div>
        </div>
      </div>
    </div>""")

    body = f"""
<div class="identity">
  <div class="wrap">
    <h1 class="gradient-text">AMERICA'S<span class="sub">SPRING CANVAS FESTIVAL</span></h1>
    <div class="where"><b>PONTIAC, MICHIGAN</b> &middot; MEMORIAL DAY WEEKEND 2028</div>
    <div class="ribbon"></div>
  </div>
</div>

<div class="hero">
  <div class="slides">{''.join(slides)}</div>
  <div class="dots" aria-label="Choose slide"></div>
</div>

<div class="ticker" aria-hidden="true">
  <div class="track">{TICKER}{TICKER}</div>
</div>

<section>
  <div class="wrap">
    <div class="mission-box">
      <div class="kicker">Community mission</div>
      <h2>Why America's Spring Canvas Festival?</h2>
      <p class="why">A four-day, family-oriented festival in Pontiac, Michigan designed to promote change &mdash;
      celebrating the cultural differences that make this nation strong, and addressing violence in our
      communities by teaching people how to resolve conflict before it escalates.</p>

      <details class="more">
        <summary>More than a festival</summary>
        <div class="inner">
          <p>America's Spring Canvas Festival is built around a simple idea: <b>conflict doesn't have to end in violence</b>.</p>
          <p>Through entertainment, education, youth engagement, art, food and community partnerships, we're
          creating an experience that brings people together while giving conflict resolution a place in the conversation.</p>
          <a class="btn btn-solid" href="{base}campaign/" data-track="cta_click" data-label="explore_campaign">EXPLORE THE CONFLICT RESOLUTION CAMPAIGN</a>
        </div>
      </details>

      <div class="execute">
        <div class="lbl">HOW WE'LL EXECUTE THE MISSION</div>
        <div class="items">
          <div><span>4</span><small>DAYS</small></div>
          <div><span>8</span><small>STAGES</small></div>
          <div><span>150+</span><small>ARTISTS &amp; EXHIBITORS</small></div>
          <div><span>50+</span><small>FOOD EXPERIENCES</small></div>
        </div>
      </div>
    </div>
  </div>
</section>

<div class="countdown" id="countdown">
  <div class="glow"></div>
  <div class="wrap">
    <div class="kicker">The canvas opens in</div>
    <div class="cd">
      <div><b data-u="d">&nbsp;</b><small>DAYS</small></div>
      <div><b data-u="h">&nbsp;</b><small>HOURS</small></div>
      <div><b data-u="m">&nbsp;</b><small>MINUTES</small></div>
      <div><b data-u="s">&nbsp;</b><small>SECONDS</small></div>
    </div>
    <div class="when">FRIDAY &middot; MAY 26, 2028 &middot; PONTIAC, MICHIGAN</div>
  </div>
</div>

<section class="alt">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Event experience</div>
      <h2>What's on the grounds.</h2>
    </div>
    <div class="cards c3">
      <a class="card" href="{base}entertainment/" data-track="card_click" data-label="entertainment">
        <div class="bar"></div>
        <div class="thumb" style="background-image:url('{base}assets/img/entertainment.svg')"></div>
        <div class="body"><h3>Entertainment</h3><p>National, regional and local stages running every day of the festival.</p><span class="more">EXPLORE &rarr;</span></div>
      </a>
      <a class="card" href="{base}exhibits/" data-track="card_click" data-label="exhibits">
        <div class="bar"></div>
        <div class="thumb" style="background-image:url('{base}assets/img/exhibits.svg')"></div>
        <div class="body"><h3>Arts &amp; Culture</h3><p>Visual arts, crafts and cultural exhibits from a hundred and fifty makers.</p><span class="more">EXPLORE &rarr;</span></div>
      </a>
      <a class="card" href="{base}eateries/" data-track="card_click" data-label="eateries">
        <div class="bar"></div>
        <div class="thumb" style="background-image:url('{base}assets/img/eateries.svg')"></div>
        <div class="body"><h3>Food</h3><p>Local restaurants, food trucks and cuisines from across the country.</p><span class="more">EXPLORE &rarr;</span></div>
      </a>
      <a class="card" href="{base}tournament/" data-track="card_click" data-label="tournament">
        <div class="bar"></div>
        <div class="thumb" style="background-image:url('{base}assets/img/tournament.svg')"></div>
        <div class="body"><h3>Competition</h3><p>The Rock/Paper/Scissors Tournament &mdash; fifty thousand contestants, four grand prizes.</p><span class="more">EXPLORE &rarr;</span></div>
      </a>
      <a class="card" href="{base}attractions/" data-track="card_click" data-label="attractions">
        <div class="bar"></div>
        <div class="thumb" style="background-image:url('{base}assets/img/attractions.svg')"></div>
        <div class="body"><h3>Attractions</h3><p>Go-karts, ninja warrior, zip line, rock climbing, Kids Zone, helicopter rides and fireworks.</p><span class="more">EXPLORE &rarr;</span></div>
      </a>
      <a class="card" href="{base}campaign/" data-track="card_click" data-label="campaign">
        <div class="bar"></div>
        <div class="thumb" style="background-image:url('{base}assets/img/mission.svg')"></div>
        <div class="body"><h3>Conflict Resolution</h3><p>The year-round campaign behind the four days.</p><span class="more">EXPLORE &rarr;</span></div>
      </a>
    </div>
  </div>
</section>
{signup_section(base, "home")}
{band(base, "Help bring the vision to life.",
      "Sponsorship and community partnership make the festival and the campaign possible.",
      "BECOME A SPONSOR", "involved/", "home_band_sponsor")}
"""
    return page("home", "America's Spring Canvas Festival &mdash; Pontiac, MI",
                "A four-day festival celebrating culture, community, entertainment and conflict resolution "
                "in Pontiac, Michigan.", body, base, "")


# ============================ INTERIOR ============================
B1 = "../"
B2 = "../../"


def mission():
    b = B1
    body = pagehead("Our purpose", "THE MISSION",
                    "A four-day festival celebrating culture, community, entertainment and conflict resolution.", wm="MISSION") + f"""
<section>
  <div class="wrap">
    <div class="split">
      <div>
        <h2>Two things at once.</h2>
        <div class="pledge" style="margin-top:22px">
          <p>The first is celebration. Our cultural differences are what make this nation strong, and the festival puts them on full display through food, art and entertainment.</p>
          <p>The second is harder. Violence in our communities often begins with a disagreement nobody knew how to end. Spring Canvas teaches people how to defuse those moments &mdash; in a way that is entertaining rather than preachy.</p>
          <p>That is why the centerpiece is a Rock Paper Scissors tournament. It is the oldest way people have settled a dispute without a fight, and we built a world-record attempt around it.</p>
        </div>
        <a class="btn btn-solid" href="{b}campaign/" data-track="cta_click" data-label="mission_to_campaign">EXPLORE THE CAMPAIGN</a>
      </div>
      <div class="ph" style="background-image:url('{b}assets/img/mission.svg')"></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="split">
      <div class="ph" style="background-image:url('{b}assets/img/banquet.svg')"></div>
      <div>
        <div class="kicker">Awards banquet &amp; forum</div>
        <h2>Honoring the peacemakers.</h2>
        <p class="lede" style="margin:18px 0">The banquet recognizes students who resolved disagreements peacefully, with a motivational keynote on how young people can address conflict before violence occurs.</p>
        <p style="color:var(--mute);font-size:14px">Keynote speaker and date <span class="tbd">TBD</span></p>
      </div>
    </div>
  </div>
</section>
{band(b, "Help us build the mission.", "Community partners help us execute the work behind the four days.", "COMMUNITY PARTNERS", "involved/partners/", "mission_band")}
"""
    return page("mission", "Mission &mdash; America's Spring Canvas Festival",
                "A four-day festival built around a conflict resolution campaign.", body, b, "mission/")


def campaign():
    b = B1
    body = pagehead("A conflict resolution campaign", "THE CAMPAIGN",
                    "Conflict doesn't have to end in violence. This is the year-round work behind the four days.", wm="CAMPAIGN") + f"""
<section>
  <div class="wrap">
    <div class="split">
      <div>
        <div class="kicker">What is the problem?</div>
        <h2>Most violence starts as<br>a disagreement.</h2>
        <p class="lede" style="margin-top:18px">Arguments between people who know each other &mdash; neighbors, classmates, family, people who shared a street corner &mdash; escalate because nobody in the moment knows how to stop them. The people involved rarely wanted it to go that far.</p>
      </div>
      <div class="ph" style="background-image:url('{b}assets/img/mission.svg')"></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">What are we trying to change?</div>
      <h2>Give conflict resolution a<br>place in the conversation.</h2>
      <p class="lede" style="margin-top:16px">Not as a lecture, a program or a pamphlet nobody reads, but as something woven into an experience people actually want to attend.</p>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">What does conflict resolution mean?</div>
      <h2>Ending it before it starts.</h2>
    </div>
    <div class="grid g3">
      <div><h3>Recognize</h3><p style="color:var(--soft);font-size:14px;margin:10px 0 0">Seeing the moment a disagreement is about to turn, before anyone has committed to it.</p></div>
      <div><h3>De-escalate</h3><p style="color:var(--soft);font-size:14px;margin:10px 0 0">Practical ways to lower the temperature &mdash; language, distance, timing, involving the right third party.</p></div>
      <div><h3>Resolve</h3><p style="color:var(--soft);font-size:14px;margin:10px 0 0">Settling the actual dispute so it doesn't return a week later as something worse.</p></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">What will we actually do?</div>
      <h2>The plan.</h2>
    </div>
    <div class="rows">
      <div class="row"><b>ANTI-VIOLENCE BILLBOARDS</b><small>SIX BOARDS OVER A SIX-MONTH PERIOD</small></div>
      <div class="row"><b>EDUCATIONAL BROCHURES</b><small>10,000 IN CIRCULATION, FOCUSED ON RESOLVING DISAGREEMENTS PEACEFULLY</small></div>
      <div class="row"><b>RADIO SPOTS</b><small>30 DAYS OF PLACEMENT</small></div>
      <div class="row"><b>STUDENT RECOGNITION</b><small>HONORING YOUNG PEOPLE WHO RESOLVED CONFLICT PEACEFULLY</small></div>
      <div class="row"><b>FORUM &amp; BANQUET</b><small>A PUBLIC CONVERSATION AND AN AWARDS NIGHT</small></div>
      <div class="row"><b>MOTIVATIONAL SPEAKERS</b><small>VOICES YOUNG PEOPLE ACTUALLY LISTEN TO</small></div>
      <div class="row"><b>YOUTH EDUCATION</b><small>PRACTICAL CONFLICT RESOLUTION, TAUGHT WHERE YOUNG PEOPLE ALREADY ARE</small></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Who we work with</div>
      <h2>Community partners &amp; programming.</h2>
    </div>
    <div data-list="partners" data-empty="campPartnersEmpty"></div>
    <div class="empty" id="campPartnersEmpty">
      <h3>Partners announced as they join</h3>
      <p>Mediation organizations, schools, nonprofits and community groups working with us on the campaign will be listed here.</p>
      <a class="btn btn-solid" href="{b}involved/partners/" data-track="cta_click" data-label="campaign_partner">BECOME A COMMUNITY PARTNER</a>
    </div>
  </div>
</section>
{band(b, "Support the campaign.", "Sponsorship funds the billboards, the brochures, the radio and the banquet.", "BECOME A SPONSOR", "involved/sponsorship/", "campaign_band")}
"""
    return page("campaign", "The Conflict Resolution Campaign &mdash; America's Spring Canvas Festival",
                "Billboards, brochures, radio, youth education and student recognition.", body, b, "campaign/")


def eateries():
    b = B1
    body = pagehead("Food", "eATERIES",
                    "Local restaurants, food trucks and cuisines from the many communities that make up America.", wm="FOOD") + f"""
<section>
  <div class="wrap">
    <div class="split">
      <div class="ph" style="background-image:url('{b}assets/img/eateries.svg')"></div>
      <div>
        <h2>Fifty kitchens.<br>Four days.</h2>
        <p class="lede" style="margin:18px 0">Every eATERY is a local business. No national chains, no concession-stand food &mdash; the same kitchens that feed this region year-round, gathered in one place for a weekend.</p>
        <p class="lede">Expect the full range: soul food, tacos, jerk, injera, banh mi, pierogi, barbecue, and whatever else shows up when you invite an entire region to cook.</p>
      </div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">The 2028 lineup</div>
      <h2>Who's cooking.</h2>
    </div>
    <div data-list="vendors" data-filter="eATERIES" data-empty="eatEmpty"></div>
    <div class="empty" id="eatEmpty">
      <h3>Vendors announced soon</h3>
      <p>The full directory goes live as restaurants are confirmed.</p>
      <a class="btn btn-solid" href="{b}contact/" data-track="cta_click" data-label="eateries_vendor_form">VENDOR INTEREST FORM</a>
    </div>
  </div>
</section>
{signup_section(b, "eateries", "Know when the vendors drop.")}
"""
    return page("eateries", "Food &mdash; America's Spring Canvas Festival",
                "Fifty local restaurants and food trucks across four days.", body, b, "eateries/")


def exhibits():
    b = B1
    body = pagehead("Arts &amp; culture", "eXHIBITS",
                    "Visual arts, crafts and cultural exhibits from a hundred and fifty artists.", wm="ART") + f"""
<section>
  <div class="wrap">
    <div class="split">
      <div>
        <h2>A market, a gallery<br>and a studio.</h2>
        <p class="lede" style="margin:18px 0">eXHIBITS is where the festival earns its name. Painting, glasswork, jewelry, printmaking, sculpture and textiles &mdash; shown, demonstrated and sold across all four days.</p>
        <p class="lede">Many artists work live on the grounds, so you can watch a piece come together and take it home the same afternoon.</p>
      </div>
      <div class="ph" style="background-image:url('{b}assets/img/exhibits.svg')"></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head"><h2>What you'll find.</h2></div>
    <div class="grid g4">
      <div><h3>Visual arts</h3><p style="color:var(--soft);font-size:14px;margin:8px 0 0">Canvas, mural and live work throughout the weekend.</p></div>
      <div><h3>Crafts</h3><p style="color:var(--soft);font-size:14px;margin:8px 0 0">Glass, jewelry, textile and woodwork from regional makers.</p></div>
      <div><h3>Cultural exhibits</h3><p style="color:var(--soft);font-size:14px;margin:8px 0 0">Organizations and communities showing their own traditions.</p></div>
      <div><h3>Print</h3><p style="color:var(--soft);font-size:14px;margin:8px 0 0">Screen printing, letterpress and limited-run works.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">The 2028 roster</div>
      <h2>Who's showing.</h2>
    </div>
    <div data-list="vendors" data-filter="eXHIBITS" data-empty="exEmpty"></div>
    <div class="empty" id="exEmpty">
      <h3>Exhibitors announced soon</h3>
      <p>Showcase your art, organization, business or cultural experience.</p>
      <a class="btn btn-solid" href="{b}contact/" data-track="cta_click" data-label="exhibits_application">EXHIBITOR APPLICATION</a>
    </div>
  </div>
</section>
{signup_section(b, "exhibits", "Know when the roster drops.")}
"""
    return page("exhibits", "Arts &amp; Culture &mdash; America's Spring Canvas Festival",
                "A hundred and fifty artists across visual arts, crafts and cultural exhibits.", body, b, "exhibits/")


def entertainment():
    b = B1
    body = pagehead("Entertainment", "eNTERTAINMENT",
                    "Eight stages running every day, from local talent at noon to national headliners at night.", wm="MUSIC") + f"""
<section>
  <div class="wrap">
    <div class="split">
      <div class="ph" style="background-image:url('{b}assets/img/entertainment.svg')"></div>
      <div>
        <h2>Eight stages.<br>Four days.</h2>
        <p class="lede" style="margin:18px 0">Acts span a wide range of musical genres, plus magic, comedy and performance throughout the grounds.</p>
      </div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head"><h2>The stages.</h2></div>
    <div class="rows">
      <div class="row"><b>NATIONAL STAGE</b><small>6,000 SEATS &middot; 12PM&ndash;11PM</small></div>
      <div class="row"><b>REGIONAL STAGE</b><small>3,000 SEATS &middot; 11AM&ndash;8PM</small></div>
      <div class="row"><b>LOCAL STAGE</b><small>1,000 SEATS &middot; 11AM&ndash;8PM</small></div>
      <div class="row"><b>GROUNDS STAGES</b><small>FIVE SMALLER STAGES ACROSS THE SITE</small></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">2028 lineup</div>
      <h2>Who's playing.</h2>
    </div>
    <div data-list="lineup" data-empty="lineupEmpty"></div>
    <div class="empty" id="lineupEmpty">
      <h3>Artists announced soon</h3>
      <p>Seven headline slots across four days. Be the first to know.</p>
      <a class="btn btn-ghost" href="{b}contact/" data-track="cta_click" data-label="perform_submit">PERFORM AT ASCF</a>
    </div>
  </div>
</section>
{signup_section(b, "lineup", "Know when the lineup drops.")}
"""
    return page("entertainment", "Entertainment &mdash; America's Spring Canvas Festival",
                "Eight stages of music, magic and comedy across four days.", body, b, "entertainment/")


def tournament():
    b = B1
    body = pagehead("Competition", "RPS TOURNAMENT",
                    "Fifty thousand contestants. Four grand prizes of $25,000. The oldest way to settle a disagreement, played at record scale.", wm="COMPETE") + f"""
<section>
  <div class="wrap">
    <div class="split">
      <div>
        <h2>Referees.<br>Announcers.<br>A world record.</h2>
        <p class="lede" style="margin:18px 0">Rock Paper Scissors is how people have settled disputes without a fight for as long as anyone can remember. We are staging it as a real sport &mdash; officiated matches, called play, and a bracket that runs the full four days.</p>
        <p class="lede">A field this size could set the world record for participants in an event of its kind.</p>
      </div>
      <div class="ph" style="background-image:url('{b}assets/img/tournament.svg')"></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="grid g4">
      <div class="stat"><span>50,000</span><small>PROJECTED CONTESTANTS</small></div>
      <div class="stat"><span>$25,000</span><small>PER GRAND PRIZE</small></div>
      <div class="stat"><span>4</span><small>GRAND PRIZES</small></div>
      <div class="stat"><span>4</span><small>DAYS OF BRACKET PLAY</small></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head"><h2>Registration.</h2></div>
    <div class="rows">
      <div class="row"><b>OPENS</b><small>DATE <span class="tbd">TBD</span></small></div>
      <div class="row"><b>ENTRY FEE</b><small><span class="tbd">TBD</span></small></div>
      <div class="row"><b>ELIGIBILITY</b><small>AGE AND RESIDENCY RULES <span class="tbd">TBD</span></small></div>
      <div class="row"><b>FORMAT</b><small>BRACKET STRUCTURE AND HEATS <span class="tbd">TBD</span></small></div>
    </div>
  </div>
</section>
{signup_section(b, "tournament", "Be first in the bracket.")}
"""
    return page("tournament", "RPS Tournament &mdash; America's Spring Canvas Festival",
                "Fifty thousand contestants competing for four $25,000 grand prizes.", body, b, "tournament/")


ATTRACTIONS = [
    ("Ninja Warrior Course", "A custom-built obstacle course designed to test every kind of fitness.", "attractions"),
    ("3-Point Shot Contest", "Make every shot from the NBA line against a 60-second clock and drive home a new car.", "attractions"),
    ("Helicopter Rides", "A once-in-a-lifetime bird's eye view of the City of Pontiac.", "attractions"),
    ("Go Karts", "A full racecourse of twists and turns for the young and the young at heart.", "attractions"),
    ("Kids Zone", "Giant coloring, slime games, puzzles and everything in between.", "kids"),
    ("Zip Line", "Height and nerve, in that order.", "attractions"),
    ("Rock Climbing", "A climbing wall for every level, from first-timers up.", "kids"),
    ("Fireworks Show", "A full sensory production lighting up the night sky.", "fireworks"),
]


def attractions():
    b = B1
    cards = "".join(f"""
      <div class="card">
        <div class="bar"></div>
        <div class="thumb" style="background-image:url('{b}assets/img/{img}.svg')"></div>
        <div class="body"><h3>{name}</h3><p>{desc}</p></div>
      </div>""" for name, desc, img in ATTRACTIONS)

    body = pagehead("Attractions", "ATTRACTIONS",
                    "The young and the young at heart get a full weekend of it.", wm="PLAY") + f"""
<section>
  <div class="wrap">
    <div class="cards c3">{cards}</div>
    <p style="color:var(--mute);font-size:13.5px;margin-top:22px">
      Height, age and weight restrictions <span class="tbd">TBD</span>. Attraction ticketing and pricing <span class="tbd">TBD</span>.
    </p>
  </div>
</section>
{band(b, "Put your brand on an attraction.", "Sponsor logos appear on co-branded event items tied to specific attractions.", "BECOME A SPONSOR", "involved/sponsorship/", "attractions_band")}
"""
    return page("attractions", "Attractions &mdash; America's Spring Canvas Festival",
                "Go-karts, ninja warrior, zip line, rock climbing, Kids Zone, helicopter rides and fireworks.",
                body, b, "attractions/")


WHY_PARTNER = [
    ("Community impact", "Your support funds billboards, brochures, radio and youth education that run all year, not just over four days."),
    ("Brand visibility", "Logo placement across the website, marketing material, news releases and co-branded event items."),
    ("Audience engagement", "A projected quarter million people over four days, with national media attention around the tournament."),
    ("Employee engagement", "Volunteer shifts, team activations and a reason for your people to be part of something in their own city."),
    ("Community investment", "A visible commitment in Pontiac, tied to a cause rather than a logo on a banner."),
    ("Media opportunities", "Press moments around the world-record attempt, the awards banquet and the campaign itself."),
]

START_CONVERSATION = [
    ("Sponsorship", "Help bring the vision to life.", "involved/sponsorship/", "SPONSORSHIP INFORMATION", "start_sponsorship"),
    ("Community Partners", "Help us build the mission.", "involved/partners/", "PARTNER WITH US", "start_partners"),
    ("Vendors", "Bring your food or business to Pontiac.", "contact/", "VENDOR INTEREST FORM", "start_vendor"),
    ("Exhibitors", "Showcase your art, organization or cultural experience.", "contact/", "EXHIBITOR APPLICATION", "start_exhibitor"),
    ("Volunteers", "Help make the experience possible.", "contact/", "VOLUNTEER", "start_volunteer"),
    ("Entertainment", "Perform at ASCF.", "contact/", "SUBMIT AN ACT", "start_entertainment"),
    ("Media", "Help tell the story.", "contact/", "MEDIA INQUIRIES", "start_media"),
    ("Donate", "Support the conflict resolution campaign.", "contact/", "DONATE", "start_donate"),
]


def involved():
    b = B1
    why = "".join(f"""
      <div><h3>{t}</h3><p style="color:var(--soft);font-size:14px;margin:10px 0 0">{d}</p></div>"""
                  for t, d in WHY_PARTNER)

    convo = "".join(f"""
      <div class="card"><div class="bar"></div><div class="body">
        <h3>{t}</h3><p>{d}</p>
        <a class="btn btn-ghost btn-block" href="{link(b, href)}" data-track="cta_click" data-label="{track}">{label}</a>
      </div></div>""" for t, d, href, label, track in START_CONVERSATION)

    body = pagehead("Get involved", "PARTNER WITH US",
                    "Four days at this scale, and a campaign that runs all year, takes a lot of hands.", wm="INVOLVED") + f"""
<section>
  <div class="wrap">
    <div class="mission-box">
      <div class="kicker">Founding partners</div>
      <h2>Become a founding partner.</h2>
      <p class="why">America's Spring Canvas Festival is bringing together entertainment, culture, community
      engagement and a year-round conflict-resolution campaign in Pontiac. Founding partners are the
      organizations that make the first one happen.</p>
      <div class="actions" style="margin-top:22px;display:flex;gap:10px;flex-wrap:wrap">
        <a class="btn btn-solid" href="{b}involved/sponsorship/" data-track="cta_click" data-label="founding_sponsorship">SPONSORSHIP INFORMATION</a>
        <a class="btn btn-ghost" href="{b}involved/partners/" data-track="cta_click" data-label="founding_partners">COMMUNITY PARTNERS</a>
      </div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Why partner with us?</div>
      <h2>Six reasons.</h2>
    </div>
    <div class="grid g3">{why}</div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">However you want in</div>
      <h2>Start the conversation.</h2>
    </div>
    <div class="cards c3">{convo}</div>
  </div>
</section>
{signup_section(b, "involved", "Stay close to the build.")}
"""
    return page("involved", "Get Involved &mdash; America's Spring Canvas Festival",
                "Founding partners, sponsorship, community partners, vendors, exhibitors, volunteers and media.",
                body, b, "involved/")


TIERS = [
    ("DIAMOND", "$250K", "var(--teal)", True),
    ("PLATINUM", "$100K", "var(--orange)", True),
    ("GOLD", "$75K", "var(--lime)", False),
    ("SILVER", "$50K", "var(--yellow)", False),
    ("BRONZE", "$25K", "#7D8688", False),
]


def sponsorship():
    b = B2
    tiers = ""
    for name, price, color, full in TIERS:
        extras = ("<li>Company giveaways allowed</li><li>Full page digital souvenir booklet ad</li>"
                  if full else "<li>Digital souvenir booklet ad</li>")
        tiers += f"""
      <div class="card" style="border-top:4px solid {color}">
        <div class="body">
          <h3 style="color:{color}">{name}</h3>
          <div style="font-family:var(--display);font-size:30px;margin-bottom:14px">{price}</div>
          <ul style="color:var(--soft);font-size:13.5px;padding-left:18px;margin:0 0 16px;line-height:1.9">
            <li>Logo placement on event website</li>
            <li>Media &amp; press opportunities</li>
            <li>Logo on event marketing material</li>
            <li>Recognition in all news releases</li>
            <li>Logo on co-branded event items</li>
            {extras}
          </ul>
        </div>
      </div>"""

    body = pagehead("Sponsorship", "BECOME A SPONSOR",
                    "Organizations providing financial and in-kind support for the festival and the campaign.", wm="SPONSOR") + f"""
<section>
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Who attends</div>
      <h2>The audience.</h2>
    </div>
    <div class="grid g4">
      <div class="stat"><span>250K+</span><small>PROJECTED OVER FOUR DAYS</small></div>
      <div class="stat"><span>50,000</span><small>TOURNAMENT CONTESTANTS</small></div>
      <div class="stat"><span>Family</span><small>MULTI-GENERATIONAL, LOCAL AND REGIONAL</small></div>
      <div class="stat"><span>National</span><small>MEDIA ATTENTION AROUND THE WORLD-RECORD ATTEMPT</small></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Brand exposure</div>
      <h2>Where your name shows up.</h2>
    </div>
    <div class="rows">
      <div class="row"><b>ON SITE</b><small>SIGNAGE, CO-BRANDED EVENT ITEMS, ATTRACTION ACTIVATIONS</small></div>
      <div class="row"><b>BROADCAST &amp; PRESS</b><small>NEWS RELEASES AND MEDIA AROUND THE WORLD-RECORD ATTEMPT</small></div>
      <div class="row"><b>CAMPAIGN MATERIAL</b><small>BILLBOARDS, 10,000 BROCHURES, 30 DAYS OF RADIO</small></div>
      <div class="row"><b>DIGITAL</b><small>WEBSITE, EMAIL ANNOUNCEMENTS AND SOCIAL CHANNELS</small></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Community impact</div>
      <h2>What your support funds.</h2>
    </div>
    <div class="grid g3">
      <div><h3>The campaign</h3><p style="color:var(--soft);font-size:14px;margin:10px 0 0">Billboards, 10,000 brochures and 30 days of radio carrying the anti-violence message.</p></div>
      <div><h3>Youth education</h3><p style="color:var(--soft);font-size:14px;margin:10px 0 0">Practical conflict resolution taught where young people already are.</p></div>
      <div><h3>Student recognition</h3><p style="color:var(--soft);font-size:14px;margin:10px 0 0">The forum and awards banquet honoring young people who chose peace.</p></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Sponsorship opportunities</div>
      <h2>Levels of support.</h2>
      <p class="lede" style="margin-top:14px">Every level can be tailored. If none of these fit what you have in mind, tell us what you're thinking.</p>
    </div>
    <div class="cards c3">{tiers}</div>
  </div>
</section>

<section data-show-list="sponsors" hidden>
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Our sponsors</div>
      <h2>Thank you to our partners.</h2>
    </div>
    <div data-list="sponsors"></div>
  </div>
</section>

<section>
  <div class="wrap" style="text-align:center">
    <h2>Request sponsorship information.</h2>
    <p class="lede" style="margin:14px auto 24px">We'll send the full deck and set up a conversation.</p>
    <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center">
      <a class="btn btn-solid" href="{b}contact/" data-track="cta_click" data-label="request_sponsorship_info">REQUEST SPONSORSHIP INFORMATION</a>
      <a class="btn btn-ghost" href="#" data-track="cta_click" data-label="download_deck">DOWNLOAD SPONSORSHIP DECK</a>
    </div>
    <p style="color:var(--mute);font-size:13px;margin-top:18px">Deck download <span class="tbd">TBD</span></p>
  </div>
</section>
"""
    return page("sponsorship", "Sponsorship &mdash; America's Spring Canvas Festival",
                "Sponsorship opportunities, audience, brand exposure and community impact.",
                body, b, "involved/sponsorship/")


def partners():
    b = B2
    body = pagehead("Community partners", "COMMUNITY PARTNERS",
                    "Organizations helping us execute the mission &mdash; not funders, but collaborators.", wm="PARTNERS") + f"""
<section>
  <div class="wrap">
    <div class="split">
      <div>
        <h2>Sponsors fund it.<br>Partners build it.</h2>
        <p class="lede" style="margin:18px 0">A community partner brings expertise, reach or programming to the conflict resolution campaign. Mediation organizations, schools, nonprofits, faith communities, government and community groups.</p>
        <p class="lede">If your work already touches conflict, youth or community safety in this region, there's a place for it here.</p>
      </div>
      <div class="ph" style="background-image:url('{b}assets/img/sponsors.svg')"></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head"><h2>What partnership looks like.</h2></div>
    <div class="grid g3">
      <div><h3>Programming</h3><p style="color:var(--soft);font-size:14px;margin:10px 0 0">Run a workshop, forum session or activation as part of the campaign.</p></div>
      <div><h3>Youth engagement</h3><p style="color:var(--soft);font-size:14px;margin:10px 0 0">Connect us with the students and young people your organization already serves.</p></div>
      <div><h3>Expertise</h3><p style="color:var(--soft);font-size:14px;margin:10px 0 0">Shape the conflict resolution material so what we teach actually holds up.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Current partners</div>
      <h2>Who we're working with.</h2>
    </div>
    <div data-list="partners" data-empty="partnersEmpty"></div>
    <div class="empty" id="partnersEmpty">
      <h3>Partners announced as they join</h3>
      <p>Confirmed community partners will be listed here with links to their work.</p>
      <a class="btn btn-solid" href="{b}contact/" data-track="cta_click" data-label="partner_inquiry">BECOME A COMMUNITY PARTNER</a>
    </div>
  </div>
</section>
"""
    return page("partners", "Community Partners &mdash; America's Spring Canvas Festival",
                "Organizations helping execute the conflict resolution mission.", body, b, "involved/partners/")


def news():
    b = B1
    body = pagehead("News &amp; updates", "LATEST NEWS",
                    "Two years is a long build. This is where the progress gets posted.", wm="NEWS") + f"""
<section>
  <div class="wrap">
    <div data-list="news" data-empty="newsEmpty"></div>
    <div class="empty" id="newsEmpty">
      <h3>First updates coming soon</h3>
      <p>Announcements, partner news, campaign milestones and behind-the-scenes progress will be posted here as the festival comes together.</p>
    </div>
  </div>
</section>
{signup_section(b, "news", "Get it in your inbox instead.")}
"""
    return page("news", "News &amp; Updates &mdash; America's Spring Canvas Festival",
                "Announcements, partner news and campaign milestones.", body, b, "news/")


CONTACTS = [
    ("General questions", "Anything that doesn't fit the categories below."),
    ("Sponsorship", "Financial and in-kind support for the festival and campaign."),
    ("Community partnership", "Organizations helping execute the mission."),
    ("Vendor", "Restaurants and food trucks interested in an eATERIES spot."),
    ("Exhibitor", "Artists, organizations and cultural exhibits."),
    ("Entertainment", "Performers looking to play one of the eight stages."),
    ("Volunteer", "Shifts across the four days."),
    ("Media", "Press credentials, interviews and story requests."),
]


def contact():
    b = B1
    cards = "".join(f"""
      <div class="contact-card">
        <h3>{t}</h3><p>{d}</p>
        <a href="mailto:" data-track="cta_click" data-label="contact_{t.lower().replace(' ', '_')}">GET IN TOUCH &rarr;</a>
      </div>""" for t, d in CONTACTS)

    body = pagehead("Contact", "GET IN TOUCH",
                    "Pick the category that fits and it reaches the right person directly.", wm="CONTACT") + f"""
<section>
  <div class="wrap">
    <div class="cards c3">{cards}</div>
    <p style="color:var(--mute);font-size:13.5px;margin-top:24px">
      Email addresses and interest forms <span class="tbd">TBD</span> &mdash; each category will route to its own
      inbox so inquiries can be tracked separately.
    </p>
  </div>
</section>
{signup_section(b, "contact")}
"""
    return page("contact", "Contact &mdash; America's Spring Canvas Festival",
                "Sponsorship, partnership, vendor, exhibitor, entertainment, volunteer and media inquiries.",
                body, b, "contact/")




def not_found():
    b = REPO_BASE   # absolute: GitHub Pages serves 404.html at whatever path was requested
    body = f"""
<section class="lost">
  <div class="wrap" style="width:100%">
    <div class="code gradient-text" style="margin:0 auto">404</div>
    <h2 style="margin-top:18px">This part of the canvas is still blank.</h2>
    <p class="lede" style="margin:14px auto 26px">The page you were looking for doesn't exist, or it moved while we were building.</p>
    <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
      <a class="btn btn-solid" href="{b}" data-track="cta_click" data-label="404_home">BACK TO HOME</a>
      <a class="btn btn-ghost" href="{b}contact/" data-track="cta_click" data-label="404_contact">CONTACT US</a>
    </div>
  </div>
</section>"""
    return page("404", "Page not found &mdash; America's Spring Canvas Festival",
                "This page doesn't exist.", body, b, "__none__", path="")

# ============================== BUILD ==============================
def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))

    pages = {
        "index.html": home(),
        "mission/index.html": mission(),
        "campaign/index.html": campaign(),
        "eateries/index.html": eateries(),
        "exhibits/index.html": exhibits(),
        "entertainment/index.html": entertainment(),
        "tournament/index.html": tournament(),
        "attractions/index.html": attractions(),
        "involved/index.html": involved(),
        "involved/sponsorship/index.html": sponsorship(),
        "involved/partners/index.html": partners(),
        "news/index.html": news(),
        "contact/index.html": contact(),
        "404.html": not_found(),
    }
    from annotate import annotate
    import json

    PAGE_NAMES = {
        "index.html": ("home", "Homepage", ""),
        "mission/index.html": ("mission", "Mission", "mission/"),
        "campaign/index.html": ("campaign", "Conflict Resolution Campaign", "campaign/"),
        "eateries/index.html": ("eateries", "Food (eATERIES)", "eateries/"),
        "exhibits/index.html": ("exhibits", "Arts & Culture (eXHIBITS)", "exhibits/"),
        "entertainment/index.html": ("entertainment", "Entertainment", "entertainment/"),
        "tournament/index.html": ("tournament", "RPS Tournament", "tournament/"),
        "attractions/index.html": ("attractions", "Attractions", "attractions/"),
        "involved/index.html": ("involved", "Get Involved", "involved/"),
        "involved/sponsorship/index.html": ("sponsorship", "Sponsorship", "involved/sponsorship/"),
        "involved/partners/index.html": ("partners", "Community Partners", "involved/partners/"),
        "news/index.html": ("news", "News", "news/"),
        "contact/index.html": ("contact", "Contact", "contact/"),
    }
    schema_pages, global_fields, seen_global = [], [], set()

    for path, html in pages.items():
        if path in PAGE_NAMES:
            pid, title, url = PAGE_NAMES[path]
            html, fields = annotate(html, pid)
            own, seen = [], set()
            for f in fields:
                if f["global"]:
                    if f["key"] not in seen_global:
                        seen_global.add(f["key"])
                        global_fields.append(f)
                    continue
                if f["key"] in seen:
                    continue
                seen.add(f["key"])
                own.append(f)
            schema_pages.append({"id": pid, "title": title, "url": url,
                                 "fields": [{k: f[k] for k in ("key", "type", "label", "section", "default")} for f in own]})
        full = os.path.join(OUT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w", encoding="utf-8").write(html)
        print("built", path)

    schema = {"pages": [{"id": "global", "title": "Site-wide (top banner & footer)", "url": "",
                         "fields": [{k: f[k] for k in ("key", "type", "label", "section", "default")}
                                    for f in global_fields]}] + schema_pages}
    with open(os.path.join(OUT, "assets", "js", "schema.js"), "w", encoding="utf-8") as fh:
        fh.write("/* Generated by build.py — do not edit by hand. */\nwindow.ASCF_SCHEMA = ")
        json.dump(schema, fh, ensure_ascii=False, indent=1)
        fh.write(";\n")
    total = sum(len(p["fields"]) for p in schema["pages"])
    print("schema:", total, "editable items across", len(schema["pages"]), "groups")

    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write("User-agent: *\nDisallow: /\n")
    open(os.path.join(OUT, ".nojekyll"), "w", encoding="utf-8").write("")

    admin_src = os.path.join(ROOT, "admin.html")
    if os.path.exists(admin_src):
        os.makedirs(os.path.join(OUT, "admin"), exist_ok=True)
        shutil.copy(admin_src, os.path.join(OUT, "admin", "index.html"))
        print("built admin/index.html")

    # The build wipes OUT every run, so the custom-domain file is recreated here.
    with open(os.path.join(OUT, "CNAME"), "w", encoding="utf-8", newline="") as fh:
        fh.write("ascfestival.com" + chr(10))
    print("built CNAME")


if __name__ == "__main__":
    main()
