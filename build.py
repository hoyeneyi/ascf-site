#!/usr/bin/env python3
"""Builds the ASCF static site. Run: python3 build.py"""
import os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "site")

NAV = [
    ("",               "Home"),
    ("mission/",       "Mission"),
    ("eateries/",      "eATERIES"),
    ("exhibits/",      "eXHIBITS"),
    ("entertainment/", "eNTERTAINMENT"),
    ("tournament/",    "Tournament"),
    ("attractions/",   "Attractions"),
    ("involved/",      "Get Involved"),
]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700'
         '&family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">')


def nav_html(base, current):
    desk, mob = [], []
    for href, label in NAV:
        cls = ' class="active"' if href == current else ""
        target = f"{base}index.html" if href == "" else f"{base}{href}"
        desk.append(f'<a href="{target}"{cls} data-track="nav_click" data-label="{label}">{label}</a>')
        mob.append(f'<a href="{target}"{cls} data-track="nav_click_mobile" data-label="{label}">{label}</a>')
    return "\n        ".join(desk), "\n      ".join(mob)


def page(slug, title, description, body, base, current=""):
    desk, mob = nav_html(base, current)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{title}</title>
<meta name="description" content="{description}">
{FONTS}
<link rel="stylesheet" href="{base}assets/css/site.css">
<script src="{base}assets/js/analytics.js"></script>
</head>
<body data-page="{slug}">

<div class="topbar">
  <div class="wrap">
    <p data-edit="banner">Be first to know when the lineup drops</p>
    <form data-signup="topbar">
      <label class="sr" for="tb-{slug}">Email address</label>
      <input id="tb-{slug}" type="email" placeholder="your@email.com" required>
      <button type="submit" data-track="cta_click" data-label="topbar_signup">KEEP ME POSTED</button>
    </form>
    <span class="ok" style="display:none"></span>
  </div>
</div>

<nav class="nav">
  <div class="wrap">
    <a class="brand" href="{base}index.html" data-track="nav_click" data-label="home">
      AMERICA'S SPRING CANVAS FESTIVAL
      <span>PONTIAC, MICHIGAN · MAY 26–29, 2028</span>
    </a>
    <div class="navlinks">
        {desk}
    </div>
    <button class="navtoggle" aria-label="Menu" aria-expanded="false"><i></i><i></i><i></i></button>
  </div>
  <div class="mobilemenu">
      {mob}
  </div>
</nav>

{body}

<footer>
  <div class="wrap">
    <div class="footgrid">
      <div>
        <div class="fbrand gradient-text">AMERICA'S<br>SPRING CANVAS FESTIVAL</div>
        <div class="meta">
          Pontiac, Michigan 48341<br>
          May 26–29, 2028 · Memorial Day Weekend<br>
          <span class="tbd">CONTACT TBD</span>
        </div>
      </div>
      <div>
        <h4>THE FESTIVAL</h4>
        <a href="{base}mission/">Mission</a>
        <a href="{base}eateries/">eATERIES</a>
        <a href="{base}exhibits/">eXHIBITS</a>
        <a href="{base}entertainment/">eNTERTAINMENT</a>
      </div>
      <div>
        <h4>TAKE PART</h4>
        <a href="{base}tournament/">RPS Tournament</a>
        <a href="{base}attractions/">Attractions</a>
        <a href="{base}involved/">Sponsor the festival</a>
        <a href="{base}involved/">Vendor &amp; artist applications</a>
      </div>
    </div>
  </div>
  <div class="footbar"></div>
</footer>

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
    <a class="btn btn-solid" href="{base}{btn_href}" data-track="cta_click" data-label="{track}">{btn_label}</a>
  </div>
</div>"""


def pagehead(kicker, h1, lede):
    return f"""
<div class="pagehead">
  <div class="glow"></div>
  <div class="wrap">
    <div class="kicker">{kicker}</div>
    <h1 class="gradient-text">{h1}</h1>
    <div class="ribbon"></div>
    <p class="lede">{lede}</p>
  </div>
</div>"""


# ============================== HOME ==============================
SLIDES = [
    ("hero-crowd", "FOUR DAYS · EIGHT STAGES",
     "Come for the<br>music.",
     "National headliners at night, local artists all afternoon, and eight stages running from noon until the fireworks.",
     [("entertainment/", "See the lineup", "btn-solid", "hero_lineup"),
      ("involved/", "Become a sponsor", "btn-ghost", "hero_sponsor")]),
    ("hero-food", "50 RESTAURANTS &amp; FOOD TRUCKS",
     "Stay for the<br>food.",
     "Fifty local kitchens serving the cooking of the communities that built this country — all of it in one place, for four days only.",
     [("eateries/", "Explore eATERIES", "btn-solid", "hero_eateries"),
      ("involved/", "Apply to vend", "btn-ghost", "hero_vend")]),
    ("hero-rps", "50,000 CONTESTANTS · 4 × $25,000",
     "Settle it the<br>old way.",
     "The largest Rock Paper Scissors tournament ever staged, with referees, announcers and four grand prizes of twenty-five thousand dollars.",
     [("tournament/", "Tournament details", "btn-solid", "hero_rps"),
      ("index.html#notify", "Get registration alerts", "btn-ghost", "hero_rps_alert")]),
    ("hero-art", "150 ARTISTS",
     "Take a piece<br>of it home.",
     "Painting, glasswork, jewelry and print from a hundred and fifty makers, showing and selling across the whole weekend.",
     [("exhibits/", "Explore eXHIBITS", "btn-solid", "hero_exhibits"),
      ("involved/", "Apply to exhibit", "btn-ghost", "hero_exhibit_apply")]),
]


def home():
    base = ""
    slides = []
    for n, (img, tag, h, p, ctas) in enumerate(SLIDES):
        buttons = "".join(
            f'<a class="btn {c}" href="{base}{href}" data-track="cta_click" data-label="{t}">{label}</a>'
            for href, label, c, t in ctas)
        slides.append(f"""
    <div class="slide{' on' if n == 0 else ''}">
      <div class="bg" style="background-image:url('{base}assets/img/{img}.svg')"></div>
      <div class="scrim"></div>
      <div class="inner wrap">
        <div class="copy">
        <span class="tag">{tag}</span>
        <h2 class="gradient-text">{h}</h2>
        <p>{p}</p>
        <div class="cta-row">{buttons}</div>
        </div>
      </div>
    </div>""")

    body = f"""
<div class="identity">
  <div class="wrap">
    <h1 class="gradient-text">AMERICA'S<span class="sub">SPRING CANVAS FESTIVAL</span></h1>
    <div class="where" data-edit="location"><b>PONTIAC, MICHIGAN</b> · MAY 26–29, 2028 · MEMORIAL DAY WEEKEND</div>
    <div class="ribbon"></div>
  </div>
</div>

<div class="hero">
  <div class="slides">{''.join(slides)}</div>
  <div class="dots" aria-label="Choose slide"></div>
</div>

<section>
  <div class="wrap">
    <div class="grid g4">
      <div class="stat"><span>4</span><small>DAYS</small></div>
      <div class="stat"><span>250K+</span><small>EXPECTED ATTENDANCE</small></div>
      <div class="stat"><span>200</span><small>VENDORS &amp; ARTISTS</small></div>
      <div class="stat"><span>8</span><small>STAGES</small></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Three ways in</div>
      <h2>Everything on the grounds.</h2>
      <p class="lede" style="margin-top:14px">Food, art and music from every culture that built this country — and one idea running through all of it.</p>
    </div>
    <div class="cards c3">
      <a class="card" href="{base}eateries/" data-track="card_click" data-label="eateries">
        <div class="bar"></div>
        <div class="thumb" style="background-image:url('{base}assets/img/eateries.svg')"></div>
        <div class="body">
          <h3>eATERIES</h3>
          <p>Fifty local restaurants and food trucks, serving four days straight.</p>
          <span class="more">EXPLORE →</span>
        </div>
      </a>
      <a class="card" href="{base}exhibits/" data-track="card_click" data-label="exhibits">
        <div class="bar"></div>
        <div class="thumb" style="background-image:url('{base}assets/img/exhibits.svg')"></div>
        <div class="body">
          <h3>eXHIBITS</h3>
          <p>A hundred and fifty artists showing and selling across every medium.</p>
          <span class="more">EXPLORE →</span>
        </div>
      </a>
      <a class="card" href="{base}entertainment/" data-track="card_click" data-label="entertainment">
        <div class="bar"></div>
        <div class="thumb" style="background-image:url('{base}assets/img/entertainment.svg')"></div>
        <div class="body">
          <h3>eNTERTAINMENT</h3>
          <p>Eight stages, national headliners and everything in between.</p>
          <span class="more">EXPLORE →</span>
        </div>
      </a>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="split">
      <div>
        <div class="kicker">Why this festival exists</div>
        <h2>A conflict resolution campaign you can dance at.</h2>
        <div class="pledge" style="margin-top:22px">
          <p>Spring Canvas carries one message: disagreements can end before they turn into violence. The festival takes that message to the people least likely to sit through a lecture about it.</p>
          <p>The campaign runs all year — billboards, print, radio, and a banquet honoring students who resolved conflict peacefully.</p>
        </div>
        <a class="btn btn-ghost" href="{base}mission/" data-track="cta_click" data-label="home_mission" style="margin-top:8px">Read the mission</a>
      </div>
      <div class="ph" style="background-image:url('{base}assets/img/mission.svg')"></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="split">
      <div class="ph" style="background-image:url('{base}assets/img/tournament.svg')"></div>
      <div>
        <div class="kicker">The main attraction</div>
        <h2>Rock. Paper.<br>Scissors.</h2>
        <p class="lede" style="margin:18px 0 22px">Fifty thousand contestants. Four grand prizes of $25,000. Referees, announcers and a bracket big enough to set a world record.</p>
        <a class="btn btn-solid" href="{base}tournament/" data-track="cta_click" data-label="home_tournament">How it works</a>
      </div>
    </div>
  </div>
</section>

<section id="notify">
  <div class="wrap" style="text-align:center">
    <div class="kicker">Stay in the loop</div>
    <h2>Lineup. Tickets. Tournament.</h2>
    <p class="lede" style="margin:14px auto 24px">One email when each announcement drops. Nothing else.</p>
    <form class="signup" data-signup="home_footer">
      <label class="sr" for="home-email">Email address</label>
      <input id="home-email" type="email" placeholder="your@email.com" required>
      <button class="btn btn-solid" type="submit" data-track="cta_click" data-label="home_signup">SIGN ME UP</button>
    </form>
    <div class="signup-note"></div>
  </div>
</section>
{band(base, "Put your brand on the canvas.",
      "Five partnership tiers reaching a projected quarter million people over four days.",
      "SPONSORSHIP OPPORTUNITIES", "involved/", "home_band_sponsor")}
"""
    return page("home", "America's Spring Canvas Festival — Pontiac, MI · May 26–29, 2028",
                "Four days of food, art and music in Pontiac, Michigan over Memorial Day weekend 2028.",
                body, base, "")


# ============================ INTERIOR ============================
B = "../"


def mission():
    body = pagehead("Our purpose", "THE MISSION",
                    "Spring Canvas is a festival with a job to do: prove that conflict does not have to end in violence.") + f"""
<section>
  <div class="wrap">
    <div class="split">
      <div>
        <h2>Two things at once.</h2>
        <div class="pledge" style="margin-top:22px">
          <p>The first is celebration. Our cultural differences are what make this nation strong, and the festival puts them on full display through food, art and entertainment.</p>
          <p>The second is harder. Violence in our communities often begins with a disagreement that nobody knew how to end. Spring Canvas teaches people how to defuse those moments — in a way that is entertaining rather than preachy.</p>
          <p>That is why the centerpiece is a Rock Paper Scissors tournament. It is the oldest way humans have settled a dispute without a fight, and we built a world-record attempt around it.</p>
        </div>
      </div>
      <div class="ph" style="background-image:url('{B}assets/img/mission.svg')"></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Beyond the four days</div>
      <h2>The year-round campaign.</h2>
    </div>
    <div class="grid g4">
      <div class="stat"><span>6</span><small>ANTI-VIOLENCE BILLBOARDS, SIX MONTHS</small></div>
      <div class="stat"><span>10,000</span><small>BROCHURES IN CIRCULATION</small></div>
      <div class="stat"><span>30</span><small>DAYS OF RADIO SPOTS</small></div>
      <div class="stat"><span>1</span><small>STUDENT AWARDS BANQUET</small></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="split">
      <div class="ph" style="background-image:url('{B}assets/img/banquet.svg')"></div>
      <div>
        <div class="kicker">Awards banquet &amp; forum</div>
        <h2>Honoring the peacemakers.</h2>
        <p class="lede" style="margin:18px 0">The banquet recognizes students who resolved disagreements peacefully, with a celebrity keynote speaker on how young people can address conflict before violence occurs.</p>
        <p style="color:var(--mute);font-size:14px">Keynote speaker and date <span class="tbd">TBD</span></p>
      </div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Charity partners</div>
      <h2>Who we stand with.</h2>
    </div>
    <div class="empty">
      <h3>Partners announced soon</h3>
      <p>Confirmed charity partners will be listed here with links to their work.</p>
    </div>
  </div>
</section>
{band(B, "Support the mission.", "Sponsorship funds the campaign, the banquet and the festival itself.", "SEE SPONSORSHIP TIERS", "involved/", "mission_band")}
"""
    return page("mission", "Mission — America's Spring Canvas Festival",
                "A four-day festival built around a conflict resolution campaign.",
                body, B, "mission/")


def eateries():
    body = pagehead("Food", "eATERIES",
                    "Fifty local restaurants and food trucks, spotlighting the cooking of the many communities that make up America.") + f"""
<section>
  <div class="wrap">
    <div class="split">
      <div class="ph" style="background-image:url('{B}assets/img/eateries.svg')"></div>
      <div>
        <h2>Fifty kitchens.<br>Four days.</h2>
        <p class="lede" style="margin:18px 0">Every eATERY is a local business. No national chains, no concession-stand food — the same kitchens that feed this region year-round, gathered in one place for a weekend.</p>
        <p class="lede">Expect the full range: soul food, tacos, jerk, injera, banh mi, pierogi, barbecue, and whatever else shows up when you invite an entire region to cook.</p>
      </div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="grid g3">
      <div class="stat"><span>50</span><small>RESTAURANTS &amp; FOOD TRUCKS</small></div>
      <div class="stat"><span>4</span><small>DAYS OF SERVICE</small></div>
      <div class="stat"><span>11am</span><small>DOORS, SATURDAY–MONDAY</small></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">The 2028 lineup</div>
      <h2>Who's cooking.</h2>
    </div>
    <div class="empty">
      <h3>Vendors announced soon</h3>
      <p>The full eATERIES directory goes live as restaurants are confirmed. Get the announcement first.</p>
      <form class="signup" data-signup="eateries">
        <label class="sr" for="eat-email">Email address</label>
        <input id="eat-email" type="email" placeholder="your@email.com" required>
        <button class="btn btn-solid" type="submit" data-track="cta_click" data-label="eateries_signup">NOTIFY ME</button>
      </form>
      <div class="signup-note"></div>
    </div>
  </div>
</section>
{band(B, "Own a restaurant or food truck?", "Applications for the fifty eATERIES spots open ahead of the 2028 festival.", "APPLY TO VEND", "involved/", "eateries_band")}
"""
    return page("eateries", "eATERIES — America's Spring Canvas Festival",
                "Fifty local restaurants and food trucks across four days.",
                body, B, "eateries/")


def exhibits():
    body = pagehead("Art", "eXHIBITS",
                    "A hundred and fifty artists celebrating the crafts and talents of cultures from across the country.") + f"""
<section>
  <div class="wrap">
    <div class="split">
      <div>
        <h2>A market, a gallery<br>and a studio.</h2>
        <p class="lede" style="margin:18px 0">eXHIBITS is where the festival earns its name. Painting, glasswork, jewelry, printmaking, sculpture, textiles — shown, demonstrated and sold across all four days.</p>
        <p class="lede">Many artists work live on the grounds, so you can watch a piece come together and take it home the same afternoon.</p>
      </div>
      <div class="ph" style="background-image:url('{B}assets/img/exhibits.svg')"></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head"><h2>What you'll find.</h2></div>
    <div class="grid g4">
      <div><h3>Painting</h3><p style="color:var(--soft);font-size:14px;margin:8px 0 0">Canvas, mural and live work throughout the weekend.</p></div>
      <div><h3>Glasswork</h3><p style="color:var(--soft);font-size:14px;margin:8px 0 0">Blown, fused and stained pieces with live demonstrations.</p></div>
      <div><h3>Jewelry</h3><p style="color:var(--soft);font-size:14px;margin:8px 0 0">Metalwork, beading and stonework from regional makers.</p></div>
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
    <div class="empty">
      <h3>Artists announced soon</h3>
      <p>The full eXHIBITS directory publishes as artists are confirmed.</p>
      <form class="signup" data-signup="exhibits">
        <label class="sr" for="ex-email">Email address</label>
        <input id="ex-email" type="email" placeholder="your@email.com" required>
        <button class="btn btn-solid" type="submit" data-track="cta_click" data-label="exhibits_signup">NOTIFY ME</button>
      </form>
      <div class="signup-note"></div>
    </div>
  </div>
</section>
{band(B, "Make something?", "A hundred and fifty exhibit spaces are open to artists in every medium.", "APPLY TO EXHIBIT", "involved/", "exhibits_band")}
"""
    return page("exhibits", "eXHIBITS — America's Spring Canvas Festival",
                "A hundred and fifty artists across painting, glass, jewelry and print.",
                body, B, "exhibits/")


def entertainment():
    body = pagehead("Music &amp; performance", "eNTERTAINMENT",
                    "Eight stages running every day of the festival, from local talent at noon to national headliners at night.") + f"""
<section>
  <div class="wrap">
    <div class="split">
      <div class="ph" style="background-image:url('{B}assets/img/entertainment.svg')"></div>
      <div>
        <h2>Eight stages.<br>Four days.</h2>
        <p class="lede" style="margin:18px 0">Acts span a wide range of musical genres, plus magic, comedy and performance throughout the grounds. The National Stage sits at the Phoenix Center Amphitheater <span class="tbd">CONFIRM</span>.</p>
      </div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="section-head"><h2>The stages.</h2></div>
    <div class="rows">
      <div class="row"><b>NATIONAL STAGE</b><small>6,000 SEATS · 12PM–11PM</small></div>
      <div class="row"><b>REGIONAL STAGE</b><small>3,000 SEATS · 11AM–8PM</small></div>
      <div class="row"><b>LOCAL STAGE</b><small>1,000 SEATS · 11AM–8PM</small></div>
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

    <div id="lineupLive" class="rows" style="display:none"></div>

    <div class="empty" id="lineupEmpty">
      <h3>Artists announced soon</h3>
      <p>Seven headline slots across four days. Leave your email and you'll know before the announcement goes public.</p>
      <form class="signup" data-signup="lineup">
        <label class="sr" for="line-email">Email address</label>
        <input id="line-email" type="email" placeholder="your@email.com" required>
        <button class="btn btn-solid" type="submit" data-track="cta_click" data-label="lineup_signup">NOTIFY ME</button>
      </form>
      <div class="signup-note"></div>
    </div>
  </div>
</section>
{band(B, "Perform at Spring Canvas.", "Local and regional acts can submit for consideration across all eight stages.", "SUBMIT YOUR ACT", "involved/", "entertainment_band")}
"""
    return page("entertainment", "eNTERTAINMENT — America's Spring Canvas Festival",
                "Eight stages of music, magic and comedy across four days.",
                body, B, "entertainment/")


def tournament():
    body = pagehead("The main attraction", "RPS TOURNAMENT",
                    "Fifty thousand contestants. Four grand prizes of $25,000. The oldest way to settle a disagreement, played at record scale.") + f"""
<section>
  <div class="wrap">
    <div class="split">
      <div>
        <h2>Referees.<br>Announcers.<br>A world record.</h2>
        <p class="lede" style="margin:18px 0">Rock Paper Scissors is how humans have settled disputes without a fight for as long as anyone can remember. We are staging it as a real sport — officiated matches, called play, and a bracket that runs the full four days.</p>
        <p class="lede">A field this size could set the world record for participants in an event of its kind.</p>
      </div>
      <div class="ph" style="background-image:url('{B}assets/img/tournament.svg')"></div>
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
    <div class="empty" style="margin-top:28px">
      <h3>Registration isn't open yet</h3>
      <p>Be first in the bracket. We'll email you the moment entries go live.</p>
      <form class="signup" data-signup="tournament">
        <label class="sr" for="rps-email">Email address</label>
        <input id="rps-email" type="email" placeholder="your@email.com" required>
        <button class="btn btn-solid" type="submit" data-track="cta_click" data-label="tournament_signup">ALERT ME</button>
      </form>
      <div class="signup-note"></div>
    </div>
  </div>
</section>
{band(B, "Sponsor the tournament.", "The main attraction draws national media across all four days.", "SPONSORSHIP TIERS", "involved/", "tournament_band")}
"""
    return page("tournament", "RPS Tournament — America's Spring Canvas Festival",
                "Fifty thousand contestants competing for four $25,000 grand prizes.",
                body, B, "tournament/")


ATTRACTIONS = [
    ("Ninja Warrior Course", "A custom-built obstacle course designed to test every kind of fitness.", "attractions"),
    ("3-Point Shot Contest", "Make every shot from the NBA line against a 60-second clock and drive home a new car.", "attractions"),
    ("Helicopter Rides", "A once-in-a-lifetime bird's eye view of the City of Pontiac.", "attractions"),
    ("Go Karts", "A full racecourse of twists and turns for the young and the young at heart.", "attractions"),
    ("Kids Zone", "Giant coloring, slime games, puzzles and everything in between.", "kids"),
    ("Zip Line &amp; Rock Wall", "Height and nerve, in that order.", "attractions"),
    ("Fireworks Show", "A full sensory production lighting up the night sky.", "fireworks"),
    ("Welcome Center", "Information, first aid, security, lost and found, tickets and giveaways.", "attractions"),
]


def attractions():
    cards = "".join(f"""
      <div class="card">
        <div class="bar"></div>
        <div class="thumb" style="background-image:url('{B}assets/img/{img}.svg')"></div>
        <div class="body"><h3>{name}</h3><p>{desc}</p></div>
      </div>""" for name, desc, img in ATTRACTIONS)

    body = pagehead("Rides, games and everything else", "ATTRACTIONS",
                    "The young and the young at heart get a full weekend of it.") + f"""
<section>
  <div class="wrap">
    <div class="cards c3">{cards}</div>
    <p style="color:var(--mute);font-size:13.5px;margin-top:22px">
      Height, age and weight restrictions for individual attractions <span class="tbd">TBD</span>.
      Ticketing and pricing for attractions <span class="tbd">TBD</span>.
    </p>
  </div>
</section>
{band(B, "Put your brand on an attraction.", "Sponsor logos appear on co-branded event items tied to specific attractions.", "SEE SPONSORSHIP TIERS", "involved/", "attractions_band")}
"""
    return page("attractions", "Attractions — America's Spring Canvas Festival",
                "Ninja warrior course, go karts, helicopter rides, Kids Zone and more.",
                body, B, "attractions/")


TIERS = [
    ("DIAMOND", "$250K", "var(--teal)", True),
    ("PLATINUM", "$100K", "var(--orange)", True),
    ("GOLD", "$75K", "var(--lime)", False),
    ("SILVER", "$50K", "var(--yellow)", False),
    ("BRONZE", "$25K", "#7D8688", False),
]


def involved():
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
          <a class="btn btn-ghost btn-block" href="#inquire" data-track="cta_click" data-label="tier_{name.lower()}">INQUIRE</a>
        </div>
      </div>"""

    body = pagehead("Get involved", "PARTNER WITH US",
                    "Sponsors, restaurants, artists and volunteers — four days at this scale takes all of it.") + f"""
<section>
  <div class="wrap">
    <div class="section-head">
      <div class="kicker">Sponsorship</div>
      <h2>Five tiers.</h2>
      <p class="lede" style="margin-top:14px">A projected quarter million people across four days, with national media coverage around the tournament.</p>
    </div>
    <div class="cards c3">{tiers}</div>
  </div>
</section>

<section class="alt" id="inquire">
  <div class="wrap">
    <div class="section-head"><h2>Start the conversation.</h2></div>
    <div class="cards c3">
      <div class="card"><div class="bar"></div><div class="body">
        <h3>Sponsors</h3><p>Tell us which tier fits and we'll send the full deck.</p>
        <a class="btn btn-ghost btn-block" href="mailto:" data-track="cta_click" data-label="sponsor_inquiry">REQUEST THE DECK</a>
      </div></div>
      <div class="card"><div class="bar"></div><div class="body">
        <h3>Restaurants &amp; food trucks</h3><p>Fifty eATERIES spots across the four days.</p>
        <a class="btn btn-ghost btn-block" href="mailto:" data-track="cta_click" data-label="vendor_apply">APPLY TO VEND</a>
      </div></div>
      <div class="card"><div class="bar"></div><div class="body">
        <h3>Artists</h3><p>A hundred and fifty exhibit spaces in every medium.</p>
        <a class="btn btn-ghost btn-block" href="mailto:" data-track="cta_click" data-label="artist_apply">APPLY TO EXHIBIT</a>
      </div></div>
      <div class="card"><div class="bar"></div><div class="body">
        <h3>Performers</h3><p>Submit your act for one of eight stages.</p>
        <a class="btn btn-ghost btn-block" href="mailto:" data-track="cta_click" data-label="performer_apply">SUBMIT AN ACT</a>
      </div></div>
      <div class="card"><div class="bar"></div><div class="body">
        <h3>Volunteers</h3><p>It takes a small city to run a festival this size.</p>
        <a class="btn btn-ghost btn-block" href="mailto:" data-track="cta_click" data-label="volunteer">VOLUNTEER</a>
      </div></div>
      <div class="card"><div class="bar"></div><div class="body">
        <h3>Media</h3><p>Press credentials and interview requests.</p>
        <a class="btn btn-ghost btn-block" href="mailto:" data-track="cta_click" data-label="press">PRESS INQUIRIES</a>
      </div></div>
    </div>
    <p style="color:var(--mute);font-size:13.5px;margin-top:22px">
      Application forms and contact addresses <span class="tbd">TBD</span> — buttons are placeholders until the client provides destinations.
    </p>
  </div>
</section>
"""
    return page("involved", "Get Involved — America's Spring Canvas Festival",
                "Sponsorship tiers, vendor and artist applications, volunteering and press.",
                body, B, "involved/")


# ============================== BUILD ==============================
def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))

    pages = {
        "index.html": home(),
        "mission/index.html": mission(),
        "eateries/index.html": eateries(),
        "exhibits/index.html": exhibits(),
        "entertainment/index.html": entertainment(),
        "tournament/index.html": tournament(),
        "attractions/index.html": attractions(),
        "involved/index.html": involved(),
    }
    for path, html in pages.items():
        full = os.path.join(OUT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w").write(html)
        print("built", path)

    # static extras
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")

    # admin portal is authored by hand, copied through
    admin_src = os.path.join(ROOT, "admin.html")
    if os.path.exists(admin_src):
        os.makedirs(os.path.join(OUT, "admin"), exist_ok=True)
        shutil.copy(admin_src, os.path.join(OUT, "admin", "index.html"))
        print("built admin/index.html")


if __name__ == "__main__":
    main()
