import re
import os

# Маппинг для генерации корректных имен файлов и слагов
COUNTRY_MAP = {
    'египет': ('Египет', 'egypt'),
    'мальдивы': ('Мальдивы', 'maldives'),
    'вьетнам': ('Вьетнам', 'vietnam'),
    'индонезия': ('Индонезия', 'indonesia'),
    'китай': ('Китай', 'china'),
    'маврикий': ('Маврикий', 'mauritius'),
    'сейшелы': ('Сейшелы', 'seychelles'),
    'таиланд': ('Таиланд', 'thailand'),
    'танзания': ('Танзания', 'tanzania'),
    'тунис': ('Тунис', 'tunisia'),
    'турция': ('Турция', 'turkey'),
    'шри-ланка': ('Шри-Ланка', 'sri-lanka')
}

def slugify(text):
    symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
               u"abvgdeejzijklmnoprstufhzcss_y_eua")
    tr = {ord(a): ord(b) for a, b in zip(*symbols)}
    text = text.lower().translate(tr)
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')

def markdown_to_html(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    lines = text.split('\n')
    output = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                output.append('</ul>')
                in_list = False
            continue
            
        if line.startswith(('- ', '● ', '* ')):
            if not in_list:
                output.append('<ul class="check-list space-y-4 mb-6 text-on-surface-variant text-lg">')
                in_list = True
            content = line[2:].strip()
            output.append(f'<li>{content}</li>')
        else:
            if in_list:
                output.append('</ul>')
                in_list = False
            output.append(f'<p class="mb-6 text-lg leading-relaxed">{line}</p>')
            
    if in_list:
        output.append('</ul>')
    return '\n'.join(output)

def create_table_from_contact(content):
    rows = []
    lines = content.split('\n')
    for line in lines:
        if ':' in line:
            key, val = line.split(':', 1)
            rows.append(f'<tr><td class="py-3 pr-4 font-bold text-black border-b border-black/5 w-1/3">{key.strip()}</td><td class="py-3 border-b border-black/5 text-on-surface">{val.strip()}</td></tr>')
    if not rows: return markdown_to_html(content)
    return f'<div class="table-container"><table class="w-full text-left text-sm"><tbody>{"".join(rows)}</tbody></table></div>'

def process_file_content(md_content):
    # Разделение на секции по [H1] или РЕГИОН:
    if 'РЕГИОН:' in md_content:
        sections_raw = re.split(r'РЕГИОН:', md_content)
    else:
        sections_raw = re.split(r'\[H1\] # ', md_content)
        
    final_content, sidebar_links, mobile_links = [], [], []
    
    for section in sections_raw:
        section = section.strip()
        if not section: continue
        lines = section.split('\n')
        title = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        if not body: continue
        
        # Удаление ФОТО: из начала тела если есть
        photo_match = re.search(r'ФОТО:\s*(.*)', body)
        photo_html = ""
        if photo_match:
            photo_url = photo_match.group(1).strip()
            # Пытаемся найти путь к картинке
            if not photo_url.startswith('http'):
                photo_url = f'../../images/{photo_url}'
            photo_html = f'<img src="{photo_url}" class="w-full h-auto rounded-[2rem] shadow-xl mb-8" loading="lazy">'
            body = re.sub(r'ФОТО:\s*.*', '', body).strip()

        section_id = slugify(title)
        html_body = create_table_from_contact(body) if any(x in title.lower() for x in ['посольство', 'телефон', 'контакты']) or (':' in body and len(body.split('\\n')) > 2) else markdown_to_html(body)
        
        section_html = f'''
        <section id="{section_id}" class="scroll-mt-32">
          <h2 class="text-3xl md:text-4xl font-black mb-8 tracking-tight">{title}</h2>
          {photo_html}
          <div class="prose prose-lg max-w-none">
            {html_body}
          </div>
        </section>
        '''
        final_content.append(section_html)
        sidebar_links.append(f'<a href="#{section_id}" class="nav-link">{title}</a>')
        mobile_links.append(f'<a href="#{section_id}" onclick="toggleMenu()" class="text-on-surface hover:text-black transition-colors py-4 border-b border-black/5 flex items-center justify-between group">{title}<span class="material-symbols-outlined opacity-20">arrow_forward</span></a>')

    return '\n'.join(final_content), '\n'.join(sidebar_links), '\n'.join(mobile_links)

def process_page(country_key, file_path, template_path, output_dir, is_memo=False):
    name_ru, slug = COUNTRY_MAP[country_key]
    print(f"Обработка {'памятки' if is_memo else 'страны'}: {name_ru} ({slug})...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_html = f.read()

    # Извлечение HERO_PHOTO если есть
    hero_match = re.search(r'HERO_PHOTO:\s*(.*)', content)
    hero_img = ""
    if hero_match:
        hero_img = hero_match.group(1).strip()
        if not hero_img.startswith('http'):
            hero_img = f'../../images/{hero_img}'
    else:
        # Fallback
        hero_urls = {
            'egypt': 'https://images.unsplash.com/photo-1572120339161-04e300ac7bb3',
            'maldives': 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8',
            'thailand': 'https://images.unsplash.com/photo-1528181304800-2f170b89892f'
        }
        hero_img = hero_urls.get(slug, 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=2673&auto=format&fit=crop')

    # Очистка контента от служебных полей для парсинга секций
    clean_content = re.sub(r'^[A-Z_]+:.*$', '', content, flags=re.MULTILINE).strip()
    if 'КОНТЕНТ' in clean_content:
        clean_content = clean_content.split('КОНТЕНТ', 1)[1].strip()

    main_html, sidebar_html, mobile_html = process_file_content(clean_content)

    html = template_html.replace('██Название██', name_ru)
    html = html.replace('██Название страны██', name_ru)
    html = html.replace('██slug██', slug)
    html = html.replace('██hero.jpg██', hero_img)
    
    html = html.replace('<!-- Ссылки -->', sidebar_html)
    html = html.replace('<!-- Мобильные ссылки -->', mobile_html)
    html = html.replace('<!-- Контент -->', main_html)
    
    # Исправление путей для вложенных директорий
    html = html.replace('href="../../index.html"', 'href="../../index.html"')
    html = html.replace('src="../../images/', 'src="../../images/')
    
    output_path = os.path.join(output_dir, f'{slug}.html')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Готово: {output_path}")

def run_splicer():
    content_dir = 'content'
    
    # 1. Обработка памяток
    template_memo = 'templates/template_memo.html'
    for filename in os.listdir(content_dir):
        if filename.startswith('Памятка_') and filename.endswith(('.txt', '.md')):
            country_ru = filename.replace('Памятка_', '').replace('.txt', '').replace('.md', '').lower()
            if country_ru in COUNTRY_MAP:
                process_page(country_ru, os.path.join(content_dir, filename), template_memo, 'pages/memos', is_memo=True)

    # 2. Обработка основных страниц стран
    template_country = 'templates/template.html'
    for filename in os.listdir(content_dir):
        # Файлы вида Египет.txt или Турция.txt (не начинаются с Памятка_)
        if not filename.startswith('Памятка_') and filename.endswith(('.txt', '.md')) and filename != 'тильда.txt' and filename != 'тильда_структура.md':
            country_ru = filename.replace('.txt', '').replace('.md', '').lower()
            if country_ru in COUNTRY_MAP:
                process_page(country_ru, os.path.join(content_dir, filename), template_country, 'pages/countries', is_memo=False)

if __name__ == "__main__":
    run_splicer()


