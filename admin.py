#!/usr/bin/env python3
"""
Emoji Tours — Админ-панель
Запуск: python admin.py
Открыть: http://localhost:5001
"""

import os, re, json
from flask import Flask, render_template_string, request, redirect, url_for, flash
from bs4 import BeautifulSoup

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML    = os.path.join(BASE_DIR, 'index.html')
MEMOS_DIR     = os.path.join(BASE_DIR, 'pages', 'memos')
COUNTRIES_DIR = os.path.join(BASE_DIR, 'pages', 'countries')
TMPL_MEMO     = os.path.join(BASE_DIR, 'templates', 'template_memo.html')
TMPL_COUNTRY  = os.path.join(BASE_DIR, 'templates', 'template.html')

app = Flask(__name__)
app.secret_key = 'emoji-tours-admin-secret'

# ─────────────────────────────────────────────
#  FILE HELPERS
# ─────────────────────────────────────────────

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_memo_slugs():
    return sorted(f[:-5] for f in os.listdir(MEMOS_DIR) if f.endswith('.html'))

# ─────────────────────────────────────────────
#  COUNTRIES (JS array in index.html)
# ─────────────────────────────────────────────

def parse_countries():
    content = read_file(INDEX_HTML)
    m = re.search(r'const countries = \[(.*?)\];', content, re.DOTALL)
    if not m:
        return []
    raw = '[' + m.group(1) + ']'
    raw = re.sub(r'(\w+):', r'"\1":', raw)
    raw = re.sub(r"'([^']*)'", r'"\1"', raw)
    raw = re.sub(r',\s*([}\]])', r'\1', raw)
    try:
        return json.loads(raw)
    except Exception:
        return []

def save_countries(countries):
    content = read_file(INDEX_HTML)
    lines = []
    for c in countries:
        sched = json.dumps(c['schedule'], ensure_ascii=False)
        lines.append(
            f'        {{ name: "{c["name"]}", emoji: "{c["emoji"]}", code: "{c["code"]}", '
            f'link: "{c["link"]}", schedule: {sched} }}'
        )
    new_block = 'const countries = [\n' + ',\n'.join(lines) + '\n      ];'
    content = re.sub(r'const countries = \[.*?\];', new_block, content, flags=re.DOTALL)
    write_file(INDEX_HTML, content)

# ─────────────────────────────────────────────
#  REVIEWS (testimonials in index.html)
# ─────────────────────────────────────────────

def parse_reviews():
    soup = BeautifulSoup(read_file(INDEX_HTML), 'html.parser')
    section = soup.find('section', id='testimonials')
    if not section:
        return []
    reviews = []
    cards = section.find_all('div', class_=lambda c: c and 'snap-center' in c)
    for i, card in enumerate(cards):
        cls = ' '.join(card.get('class', []))
        if 'min-w-[8vw]' in cls:
            continue
        author_p = card.find('p', class_=lambda c: c and 'font-bold' in c)
        trip_p   = card.find('p', class_=lambda c: c and 'opacity-60' in c)
        init_div = card.find('div', class_=lambda c: c and 'font-bold' in c and 'text-lg' in c)
        txt_cont = card.find('div', class_=lambda c: c and 'space-y-6' in c)
        paragraphs = []
        if txt_cont:
            for p in txt_cont.find_all('p', recursive=False):
                t = p.get_text(strip=True)
                if t:
                    paragraphs.append(t)
        reviews.append({
            'card_index': i,
            'author':   author_p.get_text(strip=True) if author_p else '',
            'trip':     trip_p.get_text(strip=True) if trip_p else '',
            'initials': init_div.get_text(strip=True) if init_div else '',
            'text':     '\n\n'.join(paragraphs),
        })
    return reviews

def save_review(card_index, author, trip, initials, text):
    soup = BeautifulSoup(read_file(INDEX_HTML), 'html.parser')
    section = soup.find('section', id='testimonials')
    cards = section.find_all('div', class_=lambda c: c and 'snap-center' in c)
    real_cards = [c for c in cards if 'min-w-[8vw]' not in ' '.join(c.get('class', []))]
    if card_index >= len(real_cards):
        return
    card = real_cards[card_index]

    author_p = card.find('p', class_=lambda c: c and 'font-bold' in c)
    if author_p:
        author_p.string = author

    trip_p = card.find('p', class_=lambda c: c and 'opacity-60' in c)
    if trip_p:
        trip_p.string = trip

    init_div = card.find('div', class_=lambda c: c and 'font-bold' in c and 'text-lg' in c)
    if init_div:
        init_div.string = initials

    txt_cont = card.find('div', class_=lambda c: c and 'space-y-6' in c)
    if txt_cont:
        for p in txt_cont.find_all('p', recursive=False):
            p.decompose()
        inner = txt_cont.find('div', class_=lambda c: c and 'space-y-4' in c)
        target = inner if inner else txt_cont
        for p in target.find_all('p', recursive=False):
            p.decompose()
        paragraphs = [l.strip() for l in text.split('\n\n') if l.strip()]
        for para in reversed(paragraphs):
            new_p = soup.new_tag('p')
            new_p.string = para
            target.insert(0, new_p)

    write_file(INDEX_HTML, str(soup))

# ─────────────────────────────────────────────
#  SOCIAL LINKS (footer of index.html)
# ─────────────────────────────────────────────

def parse_social():
    soup = BeautifulSoup(read_file(INDEX_HTML), 'html.parser')
    max_a   = soup.find('a', href=lambda h: h and 'max.ru' in h)
    vk_a    = soup.find('a', href=lambda h: h and 'vk.com' in h)
    phone_a = soup.find('a', href=lambda h: h and h.startswith('tel:'))
    email_a = soup.find('a', href=lambda h: h and h.startswith('mailto:'))
    return {
        'max_url': max_a['href']   if max_a   else '',
        'vk_url':  vk_a['href']    if vk_a    else '',
        'phone':   phone_a['href'].replace('tel:', '') if phone_a else '',
        'email':   email_a['href'].replace('mailto:', '') if email_a else '',
    }

def save_social(max_url, vk_url, phone, email):
    soup = BeautifulSoup(read_file(INDEX_HTML), 'html.parser')
    max_a = soup.find('a', href=lambda h: h and 'max.ru' in h)
    if max_a: max_a['href'] = max_url
    vk_a = soup.find('a', href=lambda h: h and 'vk.com' in h)
    if vk_a: vk_a['href'] = vk_url
    phone_a = soup.find('a', href=lambda h: h and h.startswith('tel:'))
    if phone_a:
        phone_a['href'] = 'tel:' + re.sub(r'\D', '', phone)
        phone_a.string = phone
    email_a = soup.find('a', href=lambda h: h and h.startswith('mailto:'))
    if email_a:
        email_a['href'] = 'mailto:' + email
        email_a.string = email
    write_file(INDEX_HTML, str(soup))

# ─────────────────────────────────────────────
#  MEMO SECTIONS
# ─────────────────────────────────────────────

def parse_memo_sections(slug):
    path = os.path.join(MEMOS_DIR, slug + '.html')
    soup = BeautifulSoup(read_file(path), 'html.parser')
    mc = soup.find('div', id='main-content')
    if not mc:
        return []
    sections = []
    for sec in mc.find_all('section', recursive=False):
        sid = sec.get('id', '')
        h2  = sec.find('h2')
        title = h2.get_text(strip=True) if h2 else sid
        sections.append({'id': sid, 'title': title, 'html': sec.decode_contents()})
    return sections

def save_memo_section(slug, section_id, new_html):
    path = os.path.join(MEMOS_DIR, slug + '.html')
    soup = BeautifulSoup(read_file(path), 'html.parser')
    sec = soup.find('section', id=section_id)
    if not sec:
        return False
    sec.clear()
    frag = BeautifulSoup(new_html, 'html.parser')
    for child in list(frag.children):
        sec.append(child)
    write_file(path, str(soup))
    return True

# ─────────────────────────────────────────────
#  ADD COUNTRY
# ─────────────────────────────────────────────

MONTH_NAMES = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
               'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

def create_country(slug, name_ru, emoji, code, schedule):
    replacements = {
        '██Название страны██': name_ru,
        'Туроператора': 'Emoji Tours',
        '██SLUG██': slug,
    }
    for src, dest_dir in [(TMPL_COUNTRY, COUNTRIES_DIR), (TMPL_MEMO, MEMOS_DIR)]:
        if not os.path.exists(src):
            continue
        t = read_file(src)
        for k, v in replacements.items():
            t = t.replace(k, v)
        write_file(os.path.join(dest_dir, slug + '.html'), t)

    countries = parse_countries()
    countries.append({
        'name': name_ru, 'emoji': emoji, 'code': code,
        'link': f'pages/countries/{slug}.html', 'schedule': schedule,
    })
    save_countries(countries)

# ─────────────────────────────────────────────
#  TEMPLATE ENGINE  (two-pass: content → layout)
# ─────────────────────────────────────────────

LAYOUT_HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{{ page_title }} — Emoji Tours Admin</title>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet"/>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: { extend: {
        colors: { primary: '#f5e2a1', secondary: '#31638a' },
        fontFamily: { sans: ['Manrope','sans-serif'] }
      }}
    }
  </script>
  <style>
    body { font-family:'Manrope',sans-serif; }
    .sl { display:flex; align-items:center; gap:8px; padding:10px 16px; border-radius:12px;
          font-weight:600; font-size:14px; color:#000; transition:background .15s; text-decoration:none; }
    .sl:hover { background:rgba(245,226,161,.4); }
    .sl.on { background:#f5e2a1; }
    .flash-ok  { background:#d1fae5; color:#065f46; }
    .flash-err { background:#fee2e2; color:#991b1b; }
    textarea.code { font-family:'Courier New',monospace; font-size:12px; line-height:1.5; }
  </style>
</head>
<body class="bg-[#fffcf5] text-black min-h-screen flex">

  <aside class="w-60 shrink-0 bg-white border-r border-black/5 min-h-screen p-5 flex flex-col gap-1.5">
    <a href="/" class="flex items-center gap-2 mb-5 no-underline">
      <span class="text-xl">🌍</span>
      <span class="font-black text-sm">Emoji Tours Admin</span>
    </a>
    <p class="text-[10px] font-black text-black/30 uppercase tracking-widest px-2 mb-0.5">Контент</p>
    <a href="/reviews"  class="sl {{ 'on' if active=='reviews' else '' }}">📝 Отзывы</a>
    <a href="/social"   class="sl {{ 'on' if active=='social' else '' }}">🔗 Соцсети / контакты</a>
    <a href="/calendar" class="sl {{ 'on' if active=='calendar' else '' }}">🗓 Страны / Календарь</a>
    <p class="text-[10px] font-black text-black/30 uppercase tracking-widest px-2 mt-3 mb-0.5">Памятки</p>
    <a href="/memos" class="sl {{ 'on' if active=='memos' else '' }}">📄 Редактировать памятки</a>
    <p class="text-[10px] font-black text-black/30 uppercase tracking-widest px-2 mt-3 mb-0.5">Действия</p>
    <a href="/add-country" class="sl {{ 'on' if active=='add-country' else '' }}">➕ Добавить страну</a>
    <div class="mt-auto pt-4 border-t border-black/5">
      <a href="/" class="text-xs text-black/30 font-bold hover:text-black">← Дашборд</a>
    </div>
  </aside>

  <main class="flex-1 p-8 max-w-5xl">
    {% for cat, msg in messages %}
      <div class="flash-{{ cat }} px-5 py-3 rounded-xl mb-5 font-semibold text-sm">{{ msg }}</div>
    {% endfor %}
    {{ page_content | safe }}
  </main>
</body>
</html>"""


def render_page(title, content_html, active=''):
    """Wrap rendered content HTML in the layout."""
    from flask import get_flashed_messages
    msgs = get_flashed_messages(with_categories=True)
    return render_template_string(
        LAYOUT_HTML,
        page_title=title,
        page_content=content_html,
        active=active,
        messages=msgs,
    )


def render_content(tmpl, **ctx):
    """Render a content-only template string with given context."""
    return render_template_string(tmpl, **ctx)


# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def dashboard():
    memos     = get_memo_slugs()
    countries = parse_countries()
    content = render_content(r"""
<h1 class="text-4xl font-black mb-1">Добро пожаловать 👋</h1>
<p class="text-black/40 mb-8 font-medium">Управление контентом Emoji Tours</p>

<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
  <div class="bg-yellow-50 border border-yellow-100 rounded-2xl p-5">
    <div class="text-3xl font-black">{{ countries|length }}</div>
    <div class="text-xs font-bold text-black/40 mt-1">Стран в календаре</div>
  </div>
  <div class="bg-yellow-50 border border-yellow-100 rounded-2xl p-5">
    <div class="text-3xl font-black">{{ memos|length }}</div>
    <div class="text-xs font-bold text-black/40 mt-1">Памяток</div>
  </div>
  <a href="/reviews" class="bg-white border border-black/5 rounded-2xl p-5 hover:bg-yellow-50 transition-colors block">
    <div class="text-xl mb-1">📝</div>
    <div class="text-sm font-bold">Отзывы</div>
  </a>
  <a href="/add-country" class="bg-white border border-black/5 rounded-2xl p-5 hover:bg-yellow-50 transition-colors block">
    <div class="text-xl mb-1">➕</div>
    <div class="text-sm font-bold">Добавить страну</div>
  </a>
</div>

<h2 class="text-lg font-black mb-3">Памятки стран</h2>
<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
  {% for slug in memos %}
  <a href="/memos/{{ slug }}"
     class="bg-white border border-black/5 rounded-xl p-3 hover:border-yellow-300 hover:bg-yellow-50 transition-all block">
    <div class="font-bold text-sm">{{ slug }}</div>
  </a>
  {% endfor %}
</div>
""", memos=memos, countries=countries)
    return render_page('Дашборд', content, active='dashboard')


# ── REVIEWS ──────────────────────────────────

@app.route('/reviews')
def reviews_page():
    reviews = parse_reviews()
    content = render_content(r"""
<h1 class="text-4xl font-black mb-1">Отзывы</h1>
<p class="text-black/40 mb-8 font-medium">Редактирование отзывов на главной странице</p>

{% for r in reviews %}
<form method="post" action="/reviews/{{ r.card_index }}/save"
      class="bg-white border border-black/5 rounded-2xl p-6 mb-5">
  <div class="flex items-center justify-between mb-4">
    <h3 class="font-black text-lg">{{ r.author or ('Отзыв ' ~ loop.index) }}</h3>
    <span class="text-xs bg-yellow-100 px-3 py-1 rounded-full font-bold">карточка #{{ r.card_index + 1 }}</span>
  </div>
  <div class="grid grid-cols-3 gap-4 mb-4">
    <div>
      <label class="block text-xs font-bold text-black/40 mb-1">Инициалы</label>
      <input name="initials" value="{{ r.initials }}"
        class="w-full border border-black/10 rounded-xl px-3 py-2 text-sm font-bold focus:outline-none focus:border-yellow-400">
    </div>
    <div>
      <label class="block text-xs font-bold text-black/40 mb-1">Имя / Фамилия</label>
      <input name="author" value="{{ r.author }}"
        class="w-full border border-black/10 rounded-xl px-3 py-2 text-sm font-bold focus:outline-none focus:border-yellow-400">
    </div>
    <div>
      <label class="block text-xs font-bold text-black/40 mb-1">Подпись (тур)</label>
      <input name="trip" value="{{ r.trip }}"
        class="w-full border border-black/10 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-yellow-400">
    </div>
  </div>
  <div>
    <label class="block text-xs font-bold text-black/40 mb-1">Текст отзыва (параграфы — через пустую строку)</label>
    <textarea name="text" rows="6"
      class="w-full border border-black/10 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-yellow-400 resize-y">{{ r.text }}</textarea>
  </div>
  <div class="flex justify-end mt-3">
    <button class="bg-black text-white px-6 py-2.5 rounded-full font-bold text-sm hover:opacity-80">Сохранить</button>
  </div>
</form>
{% endfor %}
""", reviews=reviews)
    return render_page('Отзывы', content, active='reviews')


@app.route('/reviews/<int:idx>/save', methods=['POST'])
def reviews_save(idx):
    try:
        save_review(idx,
                    request.form.get('author', ''),
                    request.form.get('trip', ''),
                    request.form.get('initials', ''),
                    request.form.get('text', ''))
        flash('Отзыв сохранён ✓', 'ok')
    except Exception as e:
        flash(f'Ошибка: {e}', 'err')
    return redirect(url_for('reviews_page'))


# ── SOCIAL ────────────────────────────────────

@app.route('/social')
def social_page():
    data = parse_social()
    content = render_content(r"""
<h1 class="text-4xl font-black mb-1">Соцсети и контакты</h1>
<p class="text-black/40 mb-8 font-medium">Ссылки и контактные данные в футере главной страницы</p>

<form method="post" action="/social/save"
      class="bg-white border border-black/5 rounded-2xl p-8 space-y-5 max-w-lg">
  <div>
    <label class="block text-xs font-bold text-black/40 mb-1">MAX — ссылка</label>
    <input name="max_url" value="{{ data.max_url }}"
      class="w-full border border-black/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-yellow-400">
  </div>
  <div>
    <label class="block text-xs font-bold text-black/40 mb-1">ВКонтакте — ссылка</label>
    <input name="vk_url" value="{{ data.vk_url }}"
      class="w-full border border-black/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-yellow-400">
  </div>
  <div>
    <label class="block text-xs font-bold text-black/40 mb-1">Телефон</label>
    <input name="phone" value="{{ data.phone }}" placeholder="+7 963-649-18-52"
      class="w-full border border-black/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-yellow-400">
  </div>
  <div>
    <label class="block text-xs font-bold text-black/40 mb-1">Email</label>
    <input name="email" value="{{ data.email }}" type="email"
      class="w-full border border-black/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-yellow-400">
  </div>
  <div class="flex justify-end pt-1">
    <button class="bg-black text-white px-8 py-3 rounded-full font-bold text-sm hover:opacity-80">Сохранить</button>
  </div>
</form>
""", data=data)
    return render_page('Соцсети', content, active='social')


@app.route('/social/save', methods=['POST'])
def social_save():
    try:
        save_social(request.form.get('max_url', ''),
                    request.form.get('vk_url', ''),
                    request.form.get('phone', ''),
                    request.form.get('email', ''))
        flash('Контакты сохранены ✓', 'ok')
    except Exception as e:
        flash(f'Ошибка: {e}', 'err')
    return redirect(url_for('social_page'))


# ── CALENDAR ──────────────────────────────────

@app.route('/calendar')
def calendar_page():
    countries = parse_countries()
    content = render_content(r"""
<div class="flex items-start justify-between mb-8">
  <div>
    <h1 class="text-4xl font-black mb-1">Страны и Календарь</h1>
    <p class="text-black/40 font-medium">Названия, эмодзи, ссылки и активности по месяцам</p>
  </div>
  <a href="/add-country"
     class="bg-black text-white px-5 py-2.5 rounded-full font-bold text-sm hover:opacity-80 shrink-0 mt-1">
    + Добавить страну
  </a>
</div>

<form method="post" action="/calendar/save">
  <input type="hidden" name="count" value="{{ countries|length }}">

  {% for ci, c in countries|enumerate %}
  <div class="bg-white border border-black/5 rounded-2xl p-5 mb-4">

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
      <div>
        <label class="block text-[10px] font-black text-black/30 uppercase tracking-widest mb-1">Название (RU)</label>
        <input name="name_{{ ci }}" value="{{ c.name }}"
          class="w-full border border-black/10 rounded-xl px-3 py-2 text-sm font-bold focus:outline-none focus:border-yellow-400">
      </div>
      <div>
        <label class="block text-[10px] font-black text-black/30 uppercase tracking-widest mb-1">Эмодзи</label>
        <input name="emoji_{{ ci }}" value="{{ c.emoji }}"
          class="w-full border border-black/10 rounded-xl px-3 py-2 text-2xl focus:outline-none focus:border-yellow-400">
      </div>
      <div>
        <label class="block text-[10px] font-black text-black/30 uppercase tracking-widest mb-1">Код (eg, th…)</label>
        <input name="code_{{ ci }}" value="{{ c.code }}"
          class="w-full border border-black/10 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-yellow-400">
      </div>
      <div>
        <label class="block text-[10px] font-black text-black/30 uppercase tracking-widest mb-1">Ссылка</label>
        <input name="link_{{ ci }}" value="{{ c.link }}"
          class="w-full border border-black/10 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-yellow-400">
      </div>
    </div>

    <p class="text-[10px] font-black text-black/25 uppercase tracking-widest mb-2">Расписание по месяцам</p>
    <div class="grid grid-cols-6 md:grid-cols-12 gap-1.5">
      {% for mi in range(12) %}
      <div class="border border-black/5 rounded-xl p-2 bg-[#fffcf5]">
        <div class="text-[10px] font-black text-black/30 text-center mb-1.5">{{ month_names[mi] }}</div>
        {% for act, icon in [('beach','🏖'),('excursion','🗺'),('ski','⛷')] %}
        <label class="flex items-center gap-1 cursor-pointer mb-0.5" title="{{ act }}">
          <input type="checkbox" name="s_{{ ci }}_{{ mi }}_{{ act }}"
            {{ 'checked' if act in c.schedule[mi] else '' }}
            class="w-3 h-3 accent-yellow-400">
          <span class="text-[11px]">{{ icon }}</span>
        </label>
        {% endfor %}
      </div>
      {% endfor %}
    </div>

  </div>
  {% endfor %}

  <div class="flex justify-end mt-2 mb-10">
    <button class="bg-black text-white px-8 py-3 rounded-full font-bold hover:opacity-80">
      Сохранить все изменения
    </button>
  </div>
</form>
""", countries=countries, month_names=MONTH_NAMES)
    return render_page('Календарь', content, active='calendar')


@app.route('/calendar/save', methods=['POST'])
def calendar_save():
    try:
        current = parse_countries()
        n = len(current)
        activities = ['beach', 'excursion', 'ski']
        updated = []
        for ci in range(n):
            schedule = []
            for mi in range(12):
                acts = [a for a in activities if request.form.get(f's_{ci}_{mi}_{a}')]
                schedule.append(acts)
            updated.append({
                'name':     request.form.get(f'name_{ci}',  current[ci]['name']),
                'emoji':    request.form.get(f'emoji_{ci}', current[ci]['emoji']),
                'code':     request.form.get(f'code_{ci}',  current[ci]['code']),
                'link':     request.form.get(f'link_{ci}',  current[ci]['link']),
                'schedule': schedule,
            })
        save_countries(updated)
        flash('Календарь сохранён ✓', 'ok')
    except Exception as e:
        flash(f'Ошибка: {e}', 'err')
    return redirect(url_for('calendar_page'))


# ── MEMOS LIST ────────────────────────────────

@app.route('/memos')
def memos_list():
    slugs = get_memo_slugs()
    content = render_content(r"""
<h1 class="text-4xl font-black mb-1">Памятки стран</h1>
<p class="text-black/40 mb-8 font-medium">Выберите памятку для редактирования разделов</p>
<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
  {% for slug in slugs %}
  <a href="/memos/{{ slug }}"
     class="bg-white border border-black/5 rounded-xl p-4 hover:border-yellow-300 hover:bg-yellow-50 transition-all block group">
    <div class="font-black text-sm group-hover:text-black">{{ slug }}</div>
    <div class="text-[11px] text-black/30 mt-0.5">pages/memos/{{ slug }}.html</div>
  </a>
  {% endfor %}
</div>
""", slugs=slugs)
    return render_page('Памятки', content, active='memos')


# ── MEMO EDITOR ───────────────────────────────

@app.route('/memos/<slug>')
def memo_edit(slug):
    sections = parse_memo_sections(slug)
    content = render_content(r"""
<div class="flex items-center gap-3 mb-7">
  <a href="/memos" class="text-sm font-bold text-black/30 hover:text-black">← Памятки</a>
  <span class="text-black/15">/</span>
  <h1 class="text-3xl font-black">{{ slug }}</h1>
  <a href="../pages/memos/{{ slug }}.html" target="_blank"
     class="ml-auto text-xs bg-black text-white px-4 py-2 rounded-full font-bold hover:opacity-70">
    Открыть ↗
  </a>
</div>

{% if not sections %}
  <div class="bg-red-50 border border-red-100 text-red-600 rounded-xl p-5 text-sm font-medium">
    Блок #main-content не найден. Разделы для редактирования недоступны.
  </div>
{% endif %}

{% for sec in sections %}
<details class="bg-white border border-black/5 rounded-2xl mb-3 overflow-hidden group">
  <summary class="flex items-center justify-between px-5 py-4 cursor-pointer select-none hover:bg-yellow-50 list-none">
    <div class="flex items-center gap-2">
      <span class="font-black">{{ sec.title }}</span>
      <span class="text-xs text-black/25 font-mono">#{{ sec.id }}</span>
    </div>
    <span class="text-black/20 text-xs font-bold group-open:hidden">▶ развернуть</span>
    <span class="text-black/20 text-xs font-bold hidden group-open:inline">▼ свернуть</span>
  </summary>
  <div class="border-t border-black/5 px-5 py-4">
    <form method="post" action="/memos/{{ slug }}/save/{{ sec.id }}">
      <label class="block text-[10px] font-black text-black/25 uppercase tracking-widest mb-2">
        HTML содержимое раздела
      </label>
      <textarea name="html_content" rows="18"
        class="code w-full border border-black/10 rounded-xl px-3 py-2.5 focus:outline-none focus:border-yellow-400 resize-y">{{ sec.html | e }}</textarea>
      <div class="flex justify-end mt-3">
        <button class="bg-black text-white px-5 py-2.5 rounded-full font-bold text-sm hover:opacity-80">
          Сохранить раздел
        </button>
      </div>
    </form>
  </div>
</details>
{% endfor %}
""", slug=slug, sections=sections)
    return render_page(f'Памятка: {slug}', content, active='memos')


@app.route('/memos/<slug>/save/<section_id>', methods=['POST'])
def memo_section_save(slug, section_id):
    try:
        ok = save_memo_section(slug, section_id, request.form.get('html_content', ''))
        flash(f'Раздел «{section_id}» сохранён ✓' if ok else f'Раздел «{section_id}» не найден', 'ok' if ok else 'err')
    except Exception as e:
        flash(f'Ошибка: {e}', 'err')
    return redirect(url_for('memo_edit', slug=slug))


# ── ADD COUNTRY ───────────────────────────────

@app.route('/add-country')
def add_country_page():
    content = render_content(r"""
<h1 class="text-4xl font-black mb-1">Добавить страну</h1>
<p class="text-black/40 mb-8 font-medium">Создаёт страницу страны и памятку из шаблонов, добавляет в календарь</p>

<form method="post" action="/add-country/create"
      class="bg-white border border-black/5 rounded-2xl p-8 max-w-2xl space-y-6">
  <div class="grid grid-cols-2 gap-5">
    <div>
      <label class="block text-xs font-bold text-black/40 mb-1">Slug (латиницей, без пробелов)</label>
      <input name="slug" required placeholder="bali"
        class="w-full border border-black/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-yellow-400">
      <p class="text-[11px] text-black/30 mt-1">Файл: pages/memos/bali.html</p>
    </div>
    <div>
      <label class="block text-xs font-bold text-black/40 mb-1">Название на русском</label>
      <input name="name_ru" required placeholder="Бали"
        class="w-full border border-black/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-yellow-400">
    </div>
    <div>
      <label class="block text-xs font-bold text-black/40 mb-1">Эмодзи-флаг</label>
      <input name="emoji" required placeholder="🇮🇩"
        class="w-full border border-black/10 rounded-xl px-4 py-3 text-2xl focus:outline-none focus:border-yellow-400">
    </div>
    <div>
      <label class="block text-xs font-bold text-black/40 mb-1">ISO-код (2 буквы)</label>
      <input name="code" required placeholder="id" maxlength="3"
        class="w-full border border-black/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-yellow-400">
    </div>
  </div>

  <div>
    <p class="text-[10px] font-black text-black/30 uppercase tracking-widest mb-3">Расписание по месяцам</p>
    <div class="grid grid-cols-6 md:grid-cols-12 gap-1.5">
      {% for mi, mn in month_names|enumerate %}
      <div class="border border-black/5 rounded-xl p-2 bg-[#fffcf5]">
        <div class="text-[10px] font-black text-black/30 text-center mb-1.5">{{ mn }}</div>
        {% for act, icon in [('beach','🏖'),('excursion','🗺'),('ski','⛷')] %}
        <label class="flex items-center gap-1 cursor-pointer mb-0.5">
          <input type="checkbox" name="s_{{ mi }}_{{ act }}" class="w-3 h-3 accent-yellow-400">
          <span class="text-[11px]">{{ icon }}</span>
        </label>
        {% endfor %}
      </div>
      {% endfor %}
    </div>
  </div>

  <div class="flex justify-end pt-1">
    <button class="bg-black text-white px-8 py-3 rounded-full font-bold hover:opacity-80">
      Создать страну →
    </button>
  </div>
</form>
""", month_names=MONTH_NAMES)
    return render_page('Добавить страну', content, active='add-country')


@app.route('/add-country/create', methods=['POST'])
def add_country_create():
    slug    = request.form.get('slug', '').strip().lower().replace(' ', '-')
    name_ru = request.form.get('name_ru', '').strip()
    emoji   = request.form.get('emoji', '').strip()
    code    = request.form.get('code', '').strip().lower()

    if not slug or not name_ru:
        flash('Заполни slug и название!', 'err')
        return redirect(url_for('add_country_page'))
    if os.path.exists(os.path.join(MEMOS_DIR, slug + '.html')):
        flash(f'Памятка «{slug}» уже существует!', 'err')
        return redirect(url_for('add_country_page'))

    activities = ['beach', 'excursion', 'ski']
    schedule = [[a for a in activities if request.form.get(f's_{mi}_{a}')] for mi in range(12)]

    try:
        create_country(slug, name_ru, emoji, code, schedule)
        flash(f'Страна «{name_ru}» создана ✓ — наполни памятку контентом', 'ok')
        return redirect(url_for('memo_edit', slug=slug))
    except Exception as e:
        flash(f'Ошибка: {e}', 'err')
        return redirect(url_for('add_country_page'))


# ─────────────────────────────────────────────
#  TEMPLATE FILTER: enumerate
# ─────────────────────────────────────────────

@app.template_filter('enumerate')
def jinja_enumerate(iterable):
    return list(enumerate(iterable))


# ─────────────────────────────────────────────

if __name__ == '__main__':
    print('\n🚀  Emoji Tours Admin Panel  →  http://localhost:5001\n')
    app.run(debug=True, port=5001)
