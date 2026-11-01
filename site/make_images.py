"""Builds optimised web images into site/assets/img from the app icon and real app screenshots.

Screenshots: rendered from the app's own web part (release build of pavel-ship-it/jewelers-hand-book,
the same pages the iOS app shows, `?embed=ios`) at 390x844 @3x, light theme, one set per language,
into site/shots/{en,ru}-<name>.png. Re-run after new screenshots: python3 site/make_images.py
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.environ.get('JH_SHOTS', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shots'))
OUT = os.path.join(HERE, 'assets', 'img')
os.makedirs(OUT, exist_ok=True)
NAMES = ['byz', 'bit', 'ruby', 'princess', 'lobster', 'carat', 'rings']
F = '/usr/share/fonts/truetype/sand-box/google/Fira Sans/'

for lang in ('en', 'ru'):
    for n in NAMES:
        im = Image.open(f'{SHOTS}/{lang}-{n}.png').convert('RGB')
        for w in (360, 720):
            im.resize((w, round(w * im.height / im.width)), Image.LANCZOS).save(f'{OUT}/{lang}-{n}-{w}.webp', 'WEBP', quality=80, method=6)

icon = Image.open(os.path.join(HERE, 'icon-1024.png')).convert('RGB')
icon.resize((192, 192), Image.LANCZOS).save(f'{OUT}/icon-192.webp', 'WEBP', quality=88)
icon.resize((512, 512), Image.LANCZOS).save(f'{OUT}/icon-512.jpg', 'JPEG', quality=90)
icon.resize((180, 180), Image.LANCZOS).save(os.path.join(HERE, 'apple-touch-icon.png'), optimize=True)
icon.resize((32, 32), Image.LANCZOS).save(os.path.join(HERE, 'favicon.png'), optimize=True)
icon.resize((48, 48), Image.LANCZOS).save(os.path.join(HERE, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])

# Open Graph cards 1200x630
TXT = {
    'en': ('Jewelers Handbook', 'Chains, stones, cuts, settings and clasps,', 'calculators and 3D models at actual size.', 'Offline · iPhone & iPad'),
    'ru': ('Справочник ювелира', 'Цепи, камни, огранки, закрепки и замки,', 'калькуляторы и 3D-модели в реальном размере.', 'Офлайн · iPhone и iPad'),
}
for lang, (title, l1, l2, l3) in TXT.items():
    W, H = 1200, 630
    og = Image.new('RGB', (W, H), '#15171c')
    d = ImageDraw.Draw(og)
    for y in range(H):  # subtle vertical gradient
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(21 + 12 * t), int(23 + 10 * t), int(28 + 6 * t)))
    glow = Image.new('L', (W, H), 0); ImageDraw.Draw(glow).ellipse((700, -200, 1400, 500), fill=90)
    og.paste(Image.new('RGB', (W, H), '#e5c07b'), (0, 0), glow.filter(ImageFilter.GaussianBlur(120)))
    ic = icon.resize((120, 120), Image.LANCZOS)
    m = Image.new('L', ic.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 119, 119), 27, fill=255)
    og.paste(ic, (70, 70), m)
    d = ImageDraw.Draw(og)
    d.text((70, 225), title, font=ImageFont.truetype(F + 'FiraSans-Bold.ttf', 66), fill='#f3dca6')
    fr = ImageFont.truetype(F + 'FiraSans-Regular.ttf', 32)
    d.text((70, 320), l1, font=fr, fill='#e9e6df'); d.text((70, 362), l2, font=fr, fill='#e9e6df')
    d.text((70, 440), l3, font=ImageFont.truetype(F + 'FiraSans-SemiBold.ttf', 28), fill='#e5c07b')
    for i, n in enumerate(('princess', 'byz')):
        s = Image.open(f'{SHOTS}/{lang}-{n}.png').convert('RGB').resize((250, 541), Image.LANCZOS)
        fr_ = Image.new('RGB', (266, 557), '#2b2f39')
        mk = Image.new('L', fr_.size, 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, 265, 556), 34, fill=255)
        sm = Image.new('L', s.size, 0); ImageDraw.Draw(sm).rounded_rectangle((0, 0, 249, 540), 27, fill=255)
        fr_.paste(s, (8, 8), sm)
        x, y = (690, 110) if i == 0 else (900, 60)
        og.paste(fr_, (x, y), mk)
    og.save(f'{OUT}/og-{lang}.jpg', 'JPEG', quality=86, optimize=True, progressive=True)
print('ok')
