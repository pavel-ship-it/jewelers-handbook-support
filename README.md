# Jewelers Handbook — support site

Source of the Jewelers Handbook mini-site: https://pavel-ship-it.github.io/jewelers-handbook-support/

GitHub Pages serves the generated `docs/` folder from `main`. Do not edit `docs/` by hand.

## Build

```sh
python3 -m venv .venv && .venv/bin/pip install jinja2 markdown pillow
.venv/bin/python site/make_images.py   # only when screenshots or the icon change
.venv/bin/python site/build.py         # regenerates docs/
```

- `site/content/{en,ru}/` — page texts (home, manual, support, FAQ, privacy, terms).
- `site/templates/` — layout and macros; `site/assets/site.css` — styles.
- `site/config.json` — base URL, App Store link (`null` until the app is published), last-modified date.
- `site/shots/` — app screenshots used by `make_images.py`.

English lives at the root, Russian under `/ru/`. The build fails if Russian text appears on an English page (except the language switcher). Canonical URLs are extensionless (`/privacy`); `/privacy.html` keeps working.
