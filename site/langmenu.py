"""Flag language switcher: <details>/<summary> popup (works without JS; JS adds Esc, arrows, click-outside)."""
FLAGS = {
    'en': ('<svg class="lsw-flag" viewBox="0 0 60 30" aria-hidden="true" focusable="false">'
           '<clipPath id="lswuk{n}"><path d="M30,15h30v15zv15h-30zh-30v-15zv-15h30z"/></clipPath>'
           '<path d="M0,0v30h60v-30z" fill="#012169"/>'
           '<path d="M0,0 60,30M60,0 0,30" stroke="#fff" stroke-width="6"/>'
           '<path d="M0,0 60,30M60,0 0,30" clip-path="url(#lswuk{n})" stroke="#C8102E" stroke-width="4"/>'
           '<path d="M30,0v30M0,15h60" stroke="#fff" stroke-width="10"/>'
           '<path d="M30,0v30M0,15h60" stroke="#C8102E" stroke-width="6"/></svg>'),
    'ru': ('<svg class="lsw-flag" viewBox="0 0 9 6" aria-hidden="true" focusable="false">'
           '<path fill="#fff" d="M0 0h9v2H0z"/><path fill="#0039A6" d="M0 2h9v2H0z"/><path fill="#D52B1E" d="M0 4h9v2H0z"/></svg>'),
}
NAMES = {'en': 'English', 'ru': 'Русский'}
CODES = {'en': 'EN', 'ru': 'RU'}
LABEL = {'en': 'Language', 'ru': 'Язык'}
ORDER = ['en', 'ru']
CARET = '<svg class="lsw-caret" viewBox="0 0 10 6" aria-hidden="true" focusable="false"><path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHECK = '<svg class="lsw-check" viewBox="0 0 12 10" aria-hidden="true" focusable="false"><path d="M1 5l3.5 3.5L11 1" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
_n = [0]

def html(cur, hrefs, key=''):
    """cur: 'en'|'ru'; hrefs: {lang: url}; key: localStorage key to remember a manual choice."""
    _n[0] += 1
    n = _n[0]
    items = []
    for l in ORDER:
        if l not in hrefs:
            continue
        curattr = ' aria-current="true"' if l == cur else ''
        items.append(f'<li><a href="{hrefs[l]}" hreflang="{l}" lang="{l}" data-lang="{l}"{curattr}>'
                     f'{FLAGS[l].format(n=f"{n}{l}")}<span>{NAMES[l]}</span>{CHECK if l == cur else ""}</a></li>')
    k = f' data-lsw-key="{key}"' if key else ''
    return (f'<details class="lsw"{k}><summary aria-haspopup="true" aria-label="{LABEL[cur]}: {NAMES[cur]}" title="{LABEL[cur]}">'
            f'{FLAGS[cur].format(n=f"{n}s")}<span class="lsw-code">{CODES[cur]}</span>{CARET}</summary>'
            f'<ul class="lsw-menu">{"".join(items)}</ul></details>')

CSS = """
/* flag language switcher */
.lsw{position:relative;display:inline-block;margin-left:4px;vertical-align:middle}
.lsw>summary{list-style:none;cursor:pointer;display:inline-flex;align-items:center;gap:7px;padding:6px 10px;border:1.5px solid var(--line,rgba(128,128,128,.35));border-radius:999px;font-weight:600;font-size:.9rem;line-height:1;user-select:none;-webkit-user-select:none;color:inherit;min-height:34px;box-sizing:border-box}
.lsw>summary::-webkit-details-marker,.lsw>summary::marker{display:none;content:""}
.lsw>summary:focus-visible{outline:2px solid currentColor;outline-offset:2px}
.lsw-flag{width:22px;height:15px;border-radius:2px;box-shadow:0 0 0 1px rgba(0,0,0,.18);flex:none;display:block;overflow:hidden}
.lsw-caret{width:10px;height:6px;flex:none;transition:transform .15s}
.lsw[open] .lsw-caret{transform:rotate(180deg)}
.lsw .lsw-menu{position:absolute;right:0;top:calc(100% + 6px);min-width:180px;margin:0;padding:6px;list-style:none;background:var(--lsw-bg,#fff);color:var(--lsw-fg,#111);border:1px solid var(--lsw-line,rgba(0,0,0,.12));border-radius:12px;box-shadow:0 12px 32px rgba(0,0,0,.22);z-index:1000;text-align:left}
.lsw .lsw-menu li{margin:0;padding:0;list-style:none}
.lsw .lsw-menu a{display:flex;align-items:center;gap:10px;padding:10px 12px;margin:0;border:0;border-radius:8px;text-decoration:none;color:inherit;font-weight:500;font-size:.95rem;white-space:nowrap;background:none;line-height:1.2}
.lsw .lsw-menu a:hover,.lsw .lsw-menu a:focus-visible{background:var(--lsw-hover,rgba(0,0,0,.07));outline:none}
.lsw .lsw-menu a[aria-current]{font-weight:700}
.lsw-check{width:12px;height:10px;margin-left:auto;flex:none}
@media (prefers-reduced-motion:reduce){.lsw-caret{transition:none}}
@media print{.lsw{display:none}}
"""

JS = r"""(function(){try{var ds=[].slice.call(document.querySelectorAll('details.lsw'));if(!ds.length)return;
ds.forEach(function(d){var s=d.querySelector('summary'),ls=[].slice.call(d.querySelectorAll('.lsw-menu a')),k=d.getAttribute('data-lsw-key');
function sync(){s.setAttribute('aria-expanded',d.open?'true':'false')}sync();d.addEventListener('toggle',sync);
d.addEventListener('keydown',function(e){var i=ls.indexOf(document.activeElement);
if(e.key==='Escape'||e.key==='Esc'){if(d.open){d.open=false;sync();s.focus();e.preventDefault()}}
else if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();if(!d.open){d.open=true;sync()}var n=i<0?(e.key==='ArrowDown'?0:ls.length-1):(i+(e.key==='ArrowDown'?1:-1)+ls.length)%ls.length;ls[n].focus()}
else if((e.key==='Home'||e.key==='End')&&i>=0){e.preventDefault();ls[e.key==='Home'?0:ls.length-1].focus()}});
d.addEventListener('focusout',function(e){if(d.open&&e.relatedTarget&&!d.contains(e.relatedTarget)){d.open=false;sync()}});
if(k)ls.forEach(function(a){a.addEventListener('click',function(){try{localStorage.setItem(k,a.getAttribute('data-lang'))}catch(x){}})})});
document.addEventListener('click',function(e){ds.forEach(function(d){if(d.open&&!d.contains(e.target)){d.open=false;d.querySelector('summary').setAttribute('aria-expanded','false')}})})}catch(x){}})();"""
