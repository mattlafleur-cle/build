#!/usr/bin/env python3
"""Builds the room pages, sitemap.xml, and event dates for buildowners.com.

Room facts live in ROOMS below. Edit them there, then run from the repo root:

    python3 tools/build_pages.py

The nav and footer are copied from index.html so every page stays in sync.
Event dates follow each room's regular rule (e.g. third Tuesday). Rerun this
every few months so the structured-data dates keep reaching ahead, and after
any cancellation or schedule change.
"""
import calendar
import datetime as dt
import html
import json
import re
from urllib.parse import quote_plus
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://buildowners.com"
TZ = ZoneInfo("America/New_York")
EVENTBRITE = "https://www.eventbrite.com/o/120744060089"
MONTHS_AHEAD = 6

ORG = {
    "@type": "Organization",
    "name": "BUILD",
    "alternateName": "Business United In Leadership Development",
    "url": SITE + "/",
}

AFF = {
    "name": "Akron Family Restaurant",
    "street": "250 W Market St",
    "city": "Akron",
    "zip": "44303",
    "phone": "330-376-0600",
}
LAPETES = {
    "name": "L.A. Pete's",
    "street": "6080 Brecksville Rd",
    "city": "Independence",
    "zip": "44131",
    "phone": None,
}

ROOMS = [
    {
        "slug": "akron-breakfast",
        "kind": "Breakfast",
        "city": "Akron",
        "h1": "Akron Business Networking Breakfast",
        "title": "Akron Business Networking Breakfast | BUILD",
        "desc": "A monthly breakfast for Akron business owners and leaders. First Tuesday at 8:00 AM at Akron Family Restaurant. Real conversation, real introductions.",
        "nth": 1, "weekday": 1, "hour": 8, "minute": 0,
        "when": "First Tuesday of the month",
        "time": "8:00 AM",
        "venue": AFF,
        "photo": "breakfast.jpg",
        "intro": "Start the month at a table of Akron business owners who have been where you are. One honest question, every voice heard, and introductions that actually happen.",
        "lat": 41.0814, "lon": -81.5190,
    },
    {
        "slug": "independence-breakfast",
        "kind": "Breakfast",
        "city": "Independence",
        "h1": "Independence Business Networking Breakfast",
        "title": "Independence Business Networking Breakfast | BUILD",
        "desc": "A monthly breakfast for business owners and leaders in Independence and the south Cleveland suburbs. Third Tuesday at 8:00 AM at L.A. Pete's.",
        "nth": 3, "weekday": 1, "hour": 8, "minute": 0,
        "when": "Third Tuesday of the month",
        "time": "8:00 AM",
        "venue": LAPETES,
        "photo": "workshop.jpg",
        "intro": "A morning table just south of Cleveland for owners who are tired of carrying the business alone. Bring your hardest question and leave with people who can help.",
        "lat": 41.3820, "lon": -81.6395,
    },
    {
        "slug": "akron-lunch",
        "kind": "Lunch",
        "city": "Akron",
        "h1": "Akron Business Networking Lunch",
        "title": "Akron Business Networking Lunch | BUILD",
        "desc": "A monthly lunch for Akron business owners and leaders who cannot do mornings. Third Tuesday at 11:30 AM at Akron Family Restaurant.",
        "nth": 3, "weekday": 1, "hour": 11, "minute": 30,
        "when": "Third Tuesday of the month",
        "time": "11:30 AM",
        "venue": AFF,
        "photo": "lunch.jpg",
        "intro": "The same BUILD table, at midday, for Akron owners whose mornings belong to the job site, the shop floor, or the kids. Same format, same honesty, a lunch menu.",
        "lat": 41.0814, "lon": -81.5190,
    },
]


def nth_weekday(year, month, nth, weekday):
    days = [d for d in calendar.Calendar().itermonthdates(year, month)
            if d.month == month and d.weekday() == weekday]
    return days[nth - 1]


def upcoming(room, start, months):
    out, y, m = [], start.year, start.month
    while len(out) < months:
        d = nth_weekday(y, m, room["nth"], room["weekday"])
        if d >= start:
            out.append(dt.datetime(d.year, d.month, d.day, room["hour"], room["minute"], tzinfo=TZ))
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def address_line(v):
    return f'{v["street"]}, {v["city"]}, OH {v["zip"]}'


def place(v):
    return {
        "@type": "Place",
        "name": v["name"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": v["street"],
            "addressLocality": v["city"],
            "addressRegion": "OH",
            "postalCode": v["zip"],
            "addressCountry": "US",
        },
    }


def maps_link(v):
    q = f'{v["name"]}, {address_line(v)}'
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(q)


def shared_chrome():
    idx = (ROOT / "index.html").read_text()
    nav = re.search(r'<nav class="nav".*?</nav>', idx, re.S).group(0)
    foot = re.search(r'<div class="stripes".*?</footer>', idx, re.S).group(0)
    fix = lambda s: s.replace('href="#', 'href="/#')
    return fix(nav), fix(foot)


FAQ_ROOM = [
    ("Who can come?",
     "Business owners and business leaders. You do not need to be a member, and you do not need to be invited. RSVP on Eventbrite so the room knows to expect you."),
    ("What happens at the table?",
     "Everyone introduces themselves with four quick answers: name, business, what you sell, and what you are looking for today. Then one real question goes in the middle of the table and the owners work it out together. It ends with a nugget round where everyone shares one takeaway or one offer to help."),
    ("Can I bring someone?",
     "Yes, please do. Every room asks members to bring another owner next time. The room works better when it grows."),
    ("What does it cost?",
     'Each room is listed on <a href="' + EVENTBRITE + '">Eventbrite</a>, and the current ticket details are shown there.'),
]


def room_page(room, nav, foot, others):
    v = room["venue"]
    dates = upcoming(room, dt.date.today(), MONTHS_AHEAD)
    url = f'{SITE}/{room["slug"]}/'
    events = [{
        "@context": "https://schema.org",
        "@type": "Event",
        "name": f'BUILD {room["kind"]} {room["city"]}',
        "description": room["desc"],
        "startDate": d.isoformat(),
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": place(v),
        "image": [f'{SITE}/assets/{room["photo"]}'],
        "organizer": ORG,
        "url": url,
    } for d in dates]
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "BUILD", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Locations", "item": SITE + "/#locations"},
            {"@type": "ListItem", "position": 3, "name": room["h1"], "item": url},
        ],
    }
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}}
                       for q, a in FAQ_ROOM],
    }
    ld = "\n".join(
        f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'
        for x in [*events, crumbs, faq_ld])
    phone = (f'<p class="sub"><a href="tel:+1{v["phone"].replace("-", "")}">{v["phone"]}</a></p>'
             if v["phone"] else "")
    static_dates = "".join(f"<li>{d.strftime('%A, %B')} {d.day}, {d.year}</li>" for d in dates[:3])
    others_html = "".join(f'''
      <a href="/{o["slug"]}/">
        <span class="label">{o["kind"]}</span>
        <h3>{o["city"]}</h3>
        <p>{o["when"]} · {o["time"]}<br>{o["venue"]["name"]}</p>
      </a>''' for o in others)
    faq_html = "".join(f"""
      <details><summary>{q}</summary><p>{a}</p></details>""" for q, a in FAQ_ROOM)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{room["title"]}</title>
<meta name="description" content="{html.escape(room["desc"])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(room["title"])}">
<meta property="og:description" content="{html.escape(room["desc"])}">
<meta property="og:image" content="{SITE}/assets/{room["photo"]}">
<meta property="og:url" content="{url}">
<meta name="theme-color" content="#231F20">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/assets/montserrat.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

{nav}

<header class="roomhero">
  <div class="wrap">
    <div>
      <p class="crumbs"><a href="/">BUILD</a> &rsaquo; <a href="/#locations">Locations</a> &rsaquo; {room["city"]} {room["kind"]}</p>
      <p class="eyebrow">BUILD {room["kind"]} · {room["city"]}, Ohio</p>
      <h1>{room["h1"]}</h1>
      <p class="lead">{room["intro"]}</p>
      <div class="cta">
        <a class="btn" href="{EVENTBRITE}">RSVP on Eventbrite</a>
        <a class="btn ghost" href="{maps_link(v)}">Get directions</a>
      </div>
    </div>
    <img class="rphoto" src="/assets/{room["photo"]}" alt="Business owners at a BUILD room" width="800" height="600">
  </div>
</header>

<main id="main">

<section class="sec" style="padding-bottom:0">
  <div class="wrap">
    <div class="facts">
      <div class="fact">
        <span class="label">When</span>
        <p>{room["when"]}</p>
        <p class="sub">{room["time"]}</p>
      </div>
      <div class="fact">
        <span class="label">Where</span>
        <p>{v["name"]}</p>
        <p class="sub">{address_line(v)}</p>
        {phone}
      </div>
      <div class="fact">
        <span class="label">Next dates</span>
        <ul class="nextdates" id="nextDates" data-nth="{room["nth"]}" data-weekday="{room["weekday"]}">{static_dates}</ul>
      </div>
      <div class="fact">
        <span class="label">Who it's for</span>
        <p>Business owners and business leaders</p>
        <p class="sub">No membership needed to attend.</p>
      </div>
    </div>
    <p class="datenote">Dates follow the regular schedule. Holidays and changes are posted on <a href="{EVENTBRITE}" style="color:var(--gold)">Eventbrite</a>, so check there before you go.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sechead">
      <div>
        <p class="eyebrow">What to expect</p>
        <h2 class="h2">Every BUILD room runs the same way.</h2>
      </div>
      <p class="lead">You are not there to hear a speaker. You are there to hear the room, and for the room to hear you.</p>
    </div>
    <div class="moves">
      <div class="move">
        <span class="label">First</span>
        <h3>Around the table</h3>
        <ol>
          <li>Your name</li>
          <li>The business you own</li>
          <li>The main thing you sell</li>
          <li>What you are looking for today</li>
        </ol>
      </div>
      <div class="move">
        <span class="label">Then</span>
        <h3>One real question</h3>
        <p>One question goes in the middle of the table, like <em>&ldquo;If you disappeared for thirty days, what would break first?&rdquo;</em> Then the room hears from the owners who have already solved it.</p>
      </div>
      <div class="move">
        <span class="label">Last</span>
        <h3>The nugget round</h3>
        <p>Everyone speaks before anyone leaves: one thing you will try, or one thing you can help with. The facilitator sends those introductions within a day.</p>
      </div>
    </div>
  </div>
</section>

<section class="sec" style="background:var(--ink-2)">
  <div class="wrap split">
    <div>
      <p class="eyebrow">Why owners come back</p>
      <h2 class="h2">Nobody builds it alone.</h2>
      <p>Most business owners spend the week alone in their own head. Not with a spouse, not with an employee, not with a vendor. A BUILD room is a table of people who have been there.</p>
      <p>BUILD exists to help business owners grow stronger businesses and stronger leaders through community, accountability, education, and strategic relationships.</p>
    </div>
    <ul class="ticks">
      <li>Peers who run businesses, not a sales pitch</li>
      <li>One honest question instead of a lecture</li>
      <li>Every person gets heard, every time</li>
      <li>Real introductions sent after the room</li>
      <li>Same day and time every month, so it fits your calendar</li>
    </ul>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">Questions</p>
    <h2 class="h2">Before your first visit</h2>
    <div class="faq">{faq_html}
    </div>
  </div>
</section>

<section class="sec" style="background:var(--ink-2)">
  <div class="wrap">
    <p class="eyebrow">Other BUILD rooms</p>
    <h2 class="h2">Can't make this one?</h2>
    <div class="morerooms">{others_html}
      <a href="/#locations">
        <span class="label">More</span>
        <h3>All locations</h3>
        <p>See every room, including the ones coming soon.</p>
      </a>
    </div>
  </div>
</section>

</main>

{foot}

<script>
(function(){{
  var ul = document.getElementById('nextDates');
  if(!ul) return;
  var nth = +ul.getAttribute('data-nth'), wd = +ul.getAttribute('data-weekday');
  var jsDay = (wd + 1) % 7;
  var now = new Date(); now.setHours(0,0,0,0);
  var out = [], y = now.getFullYear(), m = now.getMonth();
  while(out.length < 3){{
    var d = new Date(y, m, 1), count = 0;
    while(d.getMonth() === m){{
      if(d.getDay() === jsDay && ++count === nth) break;
      d.setDate(d.getDate() + 1);
    }}
    if(d >= now) out.push(d);
    if(++m > 11){{ m = 0; y++; }}
  }}
  ul.innerHTML = out.map(function(d){{
    return '<li>' + d.toLocaleDateString('en-US', {{weekday:'long', month:'long', day:'numeric', year:'numeric'}}) + '</li>';
  }}).join('');
}})();
</script>
</body>
</html>
'''


def sitemap():
    today = dt.date.today().isoformat()
    urls = [SITE + "/"] + [f'{SITE}/{r["slug"]}/' for r in ROOMS]
    body = "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n")


def main():
    nav, foot = shared_chrome()
    for r in ROOMS:
        others = [o for o in ROOMS if o is not r]
        out = ROOT / r["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(room_page(r, nav, foot, others))
        print("wrote", out.relative_to(ROOT))
    (ROOT / "sitemap.xml").write_text(sitemap())
    print("wrote sitemap.xml")


if __name__ == "__main__":
    main()
