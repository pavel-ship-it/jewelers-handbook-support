# Jewelers Handbook support site: features

This file describes the static mini-site at https://pavel-ship-it.github.io/jewelers-handbook-support/. It was written from the code on `main` at `7577996` (2026-11-01). The site describes app version 1.7.18 (`site/config.json`).

> **Location note.** This file is at the repo root, not in `docs/`. GitHub Pages publishes `docs/` publicly. `site/build.py` also deletes and regenerates `docs/` on every build, and the README says not to edit `docs/` by hand. A `docs/FEATURES.md` would therefore be public and would be wiped by the next build.

**Legend**
- **Platform:** website (all rows).
- **Verified by:**
  - **build check**: an automated check inside `site/build.py`; the build fails.
  - **manual check**: no automated test.
- The repo has no test suite.

## 1. Implemented features

| # | Feature: expected behaviour | Platform | Verified by |
|---|---|---|---|
| 1 | Static generator (`site/build.py`, Jinja2 + Markdown) regenerates `docs/` from `site/content`, `site/templates` and `site/assets`; Pages serves `main:/docs`, with `.nojekyll`. | website | manual check |
| 2 | Two languages: English at the root and Russian under `/ru/`. Every page exists in both. | website | manual check |
| 3 | No Russian text on English pages, apart from the «Русский» switcher label. The build fails otherwise. | website | build check (`check_en`) |
| 4 | Language auto-redirect: a browser with a Russian language goes to `/ru/…` on first visit, unless a choice is stored (`jh_lang`). The footer language link stores the choice. | website | manual check |
| 5 | Home page: app overview, feature cards and catalogue counts, with real app screenshots (`site/shots` → WebP 360/720 via `make_images.py`). | website | manual check |
| 6 | User manual (`/manual`): 16 sections covering getting started, home and search, chains and calculators, 3D views, actual size and calibration, stones, cuts, settings, clasps, tools, My pieces and favourites, Sources and About, language, data and offline, FAQ, and help. | website | manual check |
| 7 | Support page (`/support`): developer contact email, link to the shared support page (pavel-ship-it.github.io/support), common questions. | website | manual check |
| 8 | Privacy Policy (`/privacy`): offline, no accounts, analytics or tracking; data stays on the device; only Apple crash reports (opt-in) and support emails. Effective date 26 October 2026. | website | manual check |
| 9 | Terms of Use (`/terms`). | website | manual check |
| 10 | 404 page: English, `noindex`. | website | build check (`check_en`) |
| 11 | SEO: canonical extensionless URLs (the `.html` versions still work), `hreflang` alternates plus `x-default`, `sitemap.xml` with hreflang, `robots.txt`, Open Graph and Twitter cards (1200×630 per language), and the Google site verification tag. | website | manual check |
| 12 | Structured data (JSON-LD): MobileApplication and WebSite on home, BreadcrumbList on inner pages, FAQPage and TechArticle on the manual. | website | manual check |
| 13 | Security: a per-page meta Content-Security-Policy with inline scripts allowed by sha256 hash (computed at build), plus `no-referrer`. | website | manual check |
| 14 | Footer: «More apps by Pavel Yakimenko» (developer site) and the shared support link. | website | manual check |
| 15 | App Store link is off until the app is published (`stores.app_store: null` in `site/config.json`). | website | manual check |

## 2. Planned changes

1. **Privacy policy, website text and in-app info for iCloud sync.**
   - Pavel asked on 2026-11-08 for settings and saved projects to sync through iCloud, with the privacy policy, website text and in-app info updated to match.
   - Status: planned, not started; do not execute until Pavel asks.
   - The site currently says data stays only on the device: the privacy page, the support FAQ and the manual's "Your data and offline use" section.
2. **Clasps («Замки») on the site.**
   - On 2026-11-01 Pavel asked to hide the clasp sections from the release and the site for now. The app did this in commit `b466061`.
   - Status: **not done here.** The home page, manual (section 9 with the lobster screenshot), support page and terms still describe 14 clasp types.
   - Needs Pavel to confirm whether «с сайта» covers this support site. Do not change it without that.
3. **Privacy and support URLs** for the App Store listing: handled by Pavel with Delvi.

## 3. Features without tests
Every feature in section 1 except #3 and #10 (the build's English-page check) has no automated test: rows 1, 2, 4–9 and 11–15.
