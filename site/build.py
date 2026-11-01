#!/usr/bin/env python3
"""Builds the Jewelers Handbook website into ../docs (served by GitHub Pages from main:/docs).

Edit the sources in site/ (templates/, content/, assets/, config.json) and run:
    python3 site/build.py
Needs: jinja2, markdown  (pip install jinja2 markdown)

English lives at the root, Russian under /ru/. Canonical URLs have no .html suffix (/privacy);
GitHub Pages also serves the same file as /privacy.html, so older links keep working.
"""
import json, os, re, shutil, hashlib, html
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'docs')
CFG = json.load(open(os.path.join(HERE, 'config.json')))
BASE_URL, BASE_PATH = CFG['base_url'], CFG['base_path']
STORES = CFG['stores']
CYR = re.compile('[\u0400-\u04FF]')


def rel(u):
    return BASE_PATH + u


def abs_(u):
    return BASE_URL + BASE_PATH + u


T = {
    'en': dict(
        locale='en_US', locale_alt='ru_RU', other='ru', other_label='Русский', other_name='Русский',
        skip='Skip to content', nav_label='Main', footer_nav='Site',
        crumbs_label='Breadcrumb', nav_home='Home', nav_features='Features', nav_manual='Manual',
        nav_support='Support', nav_privacy='Privacy Policy', nav_terms='Terms of Use',
        home='/', manual='/manual/', support='/support', privacy='/privacy', terms='/terms',
        app_name='Jewelers Handbook',
        footer_tagline='An offline reference and calculator kit for jewelers, for iPhone and iPad.',
        footer_contact='Questions or ideas?',
        og_alt='Jewelers Handbook: chains, stones, cuts, settings and clasps, calculators and 3D models at actual size',
        badge_apple_small='Download on the', soon_apple='Coming soon to the App Store',
    ),
    'ru': dict(
        locale='ru_RU', locale_alt='en_US', other='en', other_label='English', other_name='English',
        skip='Перейти к содержанию', nav_label='Основное меню', footer_nav='Разделы сайта',
        crumbs_label='Навигационная цепочка', nav_home='Главная', nav_features='Возможности', nav_manual='Руководство',
        nav_support='Поддержка', nav_privacy='Политика конфиденциальности', nav_terms='Условия использования',
        home='/ru/', manual='/ru/manual/', support='/ru/support', privacy='/ru/privacy', terms='/ru/terms',
        app_name='Справочник ювелира',
        footer_tagline='Офлайн-справочник и набор калькуляторов для ювелира на iPhone и iPad.',
        footer_contact='Вопросы или идеи?',
        og_alt='Справочник ювелира: цепи, камни, огранки, закрепки и замки, калькуляторы и 3D-модели в реальном размере',
        badge_apple_small='Загрузите в', soon_apple='Скоро в App Store',
    ),
}

# key -> (en url, ru url)
URLS = {
    'home': ('/', '/ru/'), 'manual': ('/manual/', '/ru/manual/'), 'support': ('/support', '/ru/support'),
    'privacy': ('/privacy', '/ru/privacy'), 'terms': ('/terms', '/ru/terms'),
}

PAGES = {
    'en': {
        'home': dict(title='Jewelers Handbook: Offline Jewelry Reference and Calculators for iPhone & iPad',
                     og_title='Jewelers Handbook',
                     description='Chain calculators with 3D models at actual size, 32 gemstones, 15 cuts, settings, clasps, carat estimate, ring sizes and metal weight. Works offline, no account.'),
        'manual': dict(title='Jewelers Handbook User Manual: How to Use Every Section', crumb='User manual',
                       description='Step-by-step guide to Jewelers Handbook: home and search, chain calculators, 3D and actual size, stones, cuts, setting finder, clasps, carat, ring size, metal weight, My pieces and FAQ.'),
        'support': dict(title='Support – Jewelers Handbook', crumb='Support',
                        description='Get help with Jewelers Handbook for iPhone and iPad: contact the developer, report a bug, and read answers about offline use, data and calculations.'),
        'privacy': dict(title='Privacy Policy – Jewelers Handbook', crumb='Privacy Policy',
                        description='Jewelers Handbook collects no personal data. It works offline, has no accounts, ads, analytics or tracking. Only optional anonymous crash reports via Apple.'),
        'terms': dict(title='Terms of Use – Jewelers Handbook', crumb='Terms of Use',
                      description='Terms of use for the Jewelers Handbook app for iPhone and iPad: license, reference-only content, estimates and third-party sources.'),
    },
    'ru': {
        'home': dict(title='Справочник ювелира — офлайн-справочник и калькуляторы для iPhone и iPad',
                     og_title='Справочник ювелира',
                     description='Калькуляторы цепей с 3D-моделью в реальном размере, 32 камня, 15 огранок, закрепки, замки, оценка карат, размеры колец и вес металла. Без интернета и регистрации.'),
        'manual': dict(title='Руководство по «Справочнику ювелира»: как пользоваться разделами', crumb='Руководство',
                       description='Пошаговое руководство: главная и поиск, калькуляторы цепей, 3D и реальный размер, камни, огранки, подбор закрепки, замки, карат, размер кольца, вес металла, «Мои изделия» и FAQ.'),
        'support': dict(title='Поддержка – Справочник ювелира', crumb='Поддержка',
                        description='Помощь по приложению «Справочник ювелира» для iPhone и iPad: связь с разработчиком, сообщения об ошибках, ответы о работе без интернета, данных и расчётах.'),
        'privacy': dict(title='Политика конфиденциальности – Справочник ювелира', crumb='Политика конфиденциальности',
                        description='«Справочник ювелира» не собирает персональные данные. Работает офлайн, без учётных записей, рекламы, аналитики и отслеживания. Только анонимные отчёты о сбоях через Apple, если вы их разрешили.'),
        'terms': dict(title='Условия использования – Справочник ювелира', crumb='Условия использования',
                      description='Условия использования приложения «Справочник ювелира» для iPhone и iPad: лицензия, справочный характер данных, оценочные расчёты и сторонние источники.'),
    },
}

# screenshots: name -> (alt, caption) per language
SHOTS = {
    'en': {
        'byz': ('Byzantine chain calculator: a 3D model of the chain, Top view and Actual size buttons, metal, wire diameter and ring inner diameter fields', 'Byzantine chain calculator'),
        'bit': ('Moscow bit chain in 3D at actual size, with small links highlighted on every second link', 'Moscow bit in 3D'),
        'ruby': ('Ruby page: group Corundum, Mohs hardness 9, refractive index, density, colors and toughness, with a 3D model of a cut ruby', 'Stone card: ruby'),
        'princess': ('Princess cut page: facet diagram, description, fragile corners warning, sources and a 3D model of the cut', 'Cut card with 3D model'),
        'lobster': ('Lobster clasp in 3D that opens and closes, with a size field and metal choice', 'Clasps in 3D'),
        'carat': ('Size to carat estimate: a diamond next to a 1 euro cent coin for scale, with material, shape and size fields', 'Size → carat'),
        'rings': ('Ring size converter: a 3D ring and the input system, here Russia inner diameter 17 mm', 'Ring size converter'),
    },
    'ru': {
        'byz': ('Калькулятор византийской цепи: 3D-модель цепи, кнопки «Вид сверху» и «Реальный размер», поля металла, диаметра проволоки и внутреннего диаметра кольца', 'Калькулятор византийской цепи'),
        'bit': ('Московский бит в 3D в реальном размере: малые звенья на каждом втором звене выделены цветом', 'Московский бит в 3D'),
        'ruby': ('Карточка рубина: группа «корунд», твёрдость по Моосу 9, показатель преломления, плотность, цвета и вязкость, 3D-модель огранённого камня', 'Карточка камня: рубин'),
        'princess': ('Огранка «принцесса»: схема граней, описание, предупреждение об острых углах, источники и 3D-модель', 'Огранка с 3D-моделью'),
        'lobster': ('Замок-карабин «лобстер» в 3D, который открывается и закрывается, поле размера и выбор металла', 'Замки в 3D'),
        'carat': ('Оценка карат по размерам: бриллиант рядом с монетой 1 евроцент для масштаба, поля материала, формы и размеров', 'Размер → карат'),
        'rings': ('Конвертер размеров кольца: 3D-кольцо и выбор системы, здесь РФ, внутренний диаметр 17 мм', 'Размер кольца'),
    },
}


def strip_tags(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()


def ld(obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    return Markup(s.replace('</', '<\\/'))


def out_path(url):
    p = url.lstrip('/')
    if p == '' or p.endswith('/'):
        return os.path.join(OUT, p, 'index.html')
    return os.path.join(OUT, p + '.html')


def md_page(lang, key):
    src = open(os.path.join(HERE, 'content', lang, key + '.md'), encoding='utf-8').read()
    src = re.sub(r"\{\{\s*'([^']+)'\s*\|\s*relative_url\s*\}\}", lambda m: rel(m.group(1)), src)
    body = markdown.markdown(src, extensions=['tables', 'sane_lists'])
    body = body.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    body = body.replace('<a href="http', '<a rel="noopener" href="http')
    return f'<article class="wrap narrow doc">\n{body}\n</article>'


def check_en(path, text):
    """English pages may contain Russian only in the language switcher label."""
    t = re.sub(r'<script type="application/ld\+json">.*?</script>', '', text, flags=re.S)
    t = t.replace('>Русский<', '><')
    bad = sorted(set(m.group(0) for m in re.finditer(r'\S*[\u0400-\u04FF]\S*', t)))
    if bad or CYR.search(text.replace('>Русский<', '><')):
        raise SystemExit(f'Russian text on an English page {path}: {bad[:10]}')


def main():
    env = Environment(loader=FileSystemLoader([os.path.join(HERE, 'templates'), os.path.join(HERE, 'content')]),
                      autoescape=select_autoescape(['html']), trim_blocks=False, lstrip_blocks=False)
    css = open(os.path.join(HERE, 'assets', 'site.css'), 'rb').read()
    env.globals.update(rel=rel, abs=abs_, stores=STORES, css_version=hashlib.md5(css).hexdigest()[:8],
                       app_version=CFG['app_version'])

    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(HERE, 'assets'), os.path.join(OUT, 'assets'))
    for f in ('favicon.ico', 'favicon.png', 'apple-touch-icon.png'):
        shutil.copy(os.path.join(HERE, f), OUT)
    open(os.path.join(OUT, '.nojekyll'), 'w').close()

    sitemap = []
    for lang in ('en', 'ru'):
        t = T[lang]
        faq = json.load(open(os.path.join(HERE, 'content', lang, 'faq.json'), encoding='utf-8'))
        for key, meta in PAGES[lang].items():
            url = URLS[key][0 if lang == 'en' else 1]
            page = dict(meta, url=url, kind=key, alternates={'en': URLS[key][0], 'ru': URLS[key][1]}, jsonld=[])
            if key != 'home':
                page['crumbs'] = [(t['nav_home'], t['home']), (meta['crumb'], url)]
                page['jsonld'].append(ld({
                    '@context': 'https://schema.org', '@type': 'BreadcrumbList',
                    'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': abs_(u)}
                                        for i, (n, u) in enumerate(page['crumbs'])]}))
            ctx = dict(lang=lang, t=t, page=page, faq=faq, shots=SHOTS[lang])
            if key == 'home':
                page['jsonld'].insert(0, ld(home_ld(lang, page)))
                body = env.get_template(f'{lang}/home.html').render(**ctx)
            elif key in ('manual', 'support'):
                if key == 'manual':
                    page['jsonld'].append(ld({
                        '@context': 'https://schema.org', '@type': 'FAQPage', 'inLanguage': lang,
                        'mainEntity': [{'@type': 'Question', 'name': strip_tags(q['q']),
                                        'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(q['a'])}} for q in faq]}))
                    page['jsonld'].append(ld({
                        '@context': 'https://schema.org', '@type': 'TechArticle', 'headline': meta['title'],
                        'description': meta['description'], 'inLanguage': lang, 'url': abs_(url),
                        'dateModified': CFG['lastmod'], 'image': abs_('/assets/img/og-' + lang + '.jpg'),
                        'author': {'@type': 'Person', 'name': 'Pavel Yakimenko'},
                        'about': {'@id': abs_(t['home'] + '#app')}}))
                body = env.get_template(f'{lang}/{key}.html').render(**ctx)
            else:
                body = md_page(lang, key)
            html_out = env.get_template('base.html').render(body=Markup(body), **ctx)
            p = out_path(url)
            if lang == 'en':
                check_en(p, html_out)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'w', encoding='utf-8').write(html_out)
            if lang == 'en':
                sitemap.append(key)

    # 404 (English, noindex; the switcher label is the only Russian word)
    page = dict(title='Page not found – Jewelers Handbook', description='This page does not exist. Go to the Jewelers Handbook home page, manual or support.',
                url='/404', kind='404', alternates={'en': '/', 'ru': '/ru/'}, jsonld=[], robots='noindex')
    html404 = env.get_template('base.html').render(body=Markup(env.get_template('404.html').render(lang='en', t=T['en'], page=page)),
                                                   lang='en', t=T['en'], page=page)
    check_en('404.html', html404)
    open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(html404)

    prio = {'home': '1.0', 'manual': '0.9', 'support': '0.8', 'privacy': '0.5', 'terms': '0.3'}
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for key in sitemap:
        en, ru = URLS[key]
        for u in (en, ru):
            lines += ['  <url>', f'    <loc>{abs_(u)}</loc>', f'    <lastmod>{CFG["lastmod"]}</lastmod>',
                      f'    <priority>{prio[key]}</priority>',
                      f'    <xhtml:link rel="alternate" hreflang="en" href="{abs_(en)}"/>',
                      f'    <xhtml:link rel="alternate" hreflang="ru" href="{abs_(ru)}"/>',
                      f'    <xhtml:link rel="alternate" hreflang="x-default" href="{abs_(en)}"/>', '  </url>']
    lines.append('</urlset>')
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write('\n'.join(lines) + '\n')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {abs_("/sitemap.xml")}\n')
    print('built', len(sitemap) * 2, 'pages + 404 into', OUT)


def home_ld(lang, page):
    en = lang == 'en'
    feats = {
        'en': ['Chain calculators: Byzantine, anchor (cable) and Moscow bit with rings, wire and weight and a 3D model at actual size',
               'Approximate weight for Bismarck, rope, curb, Figaro and box chains',
               '32 gemstones: hardness, toughness, refractive index, density, treatments and cleaning',
               '15 cuts with 3D models and fragile spots',
               'Setting types and a setting finder by stone and cut',
               '14 clasp types with 3D diagrams that open and close',
               'Size to carat estimate, ring size converter (EU, RU, US, UK) and metal weight',
               'Actual-size mode, automatic on known iPhones and iPads',
               'My pieces, favorites and search in English and Russian; works offline, no account'],
        'ru': ['Калькуляторы цепей: византийская, якорная и «Московский бит» — кольца, проволока, вес и 3D-модель в реальном размере',
               'Примерный вес бисмарка, верёвочки, панциря, фигаро и коробочки',
               '32 камня: твёрдость, вязкость, преломление, плотность, облагораживание и чистка',
               '15 огранок с 3D-моделями и хрупкими местами',
               'Типы закрепок и подбор закрепки по камню и огранке',
               '14 типов замков с 3D-схемами, которые открываются и закрываются',
               'Оценка карат по размерам, размеры колец (EU, РФ, US, UK) и вес металла',
               'Реальный размер на экране, автоматически на известных iPhone и iPad',
               '«Мои изделия», избранное и поиск на русском и английском; офлайн, без регистрации'],
    }
    app = {
        '@type': 'MobileApplication', '@id': abs_(page['url'] + '#app'),
        'name': 'Jewelers Handbook' if en else 'Справочник ювелира',
        'alternateName': 'Справочник ювелира' if not en else "Jeweler's Handbook",
        'description': page['description'], 'url': abs_(page['url']),
        'operatingSystem': 'iOS, iPadOS', 'applicationCategory': 'ReferenceApplication',
        'softwareVersion': CFG['app_version'], 'image': abs_('/assets/img/icon-512.jpg'),
        'screenshot': [abs_(f'/assets/img/{lang}-{n}-720.webp') for n in SHOTS[lang]],
        'featureList': feats[lang], 'inLanguage': ['en', 'ru'],
        'offers': None,
        'author': {'@type': 'Person', 'name': 'Pavel Yakimenko', 'email': 'mailto:dreamcomenull@gmail.com'},
        'publisher': {'@type': 'Person', 'name': 'Pavel Yakimenko'},
    }
    del app['offers']
    if STORES.get('app_store'):
        app['sameAs'] = [STORES['app_store']]
        app['installUrl'] = STORES['app_store']
    site = {'@type': 'WebSite', '@id': abs_(page['url'] + '#website'), 'name': 'Jewelers Handbook' if en else 'Справочник ювелира',
            'url': abs_(page['url']), 'inLanguage': lang, 'publisher': {'@type': 'Person', 'name': 'Pavel Yakimenko'}}
    return {'@context': 'https://schema.org', '@graph': [site, app]}


if __name__ == '__main__':
    main()
