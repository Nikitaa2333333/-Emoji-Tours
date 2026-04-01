import os, re, sys, glob

# Мэппинг для URL (транслитерация)
SLUGS = {
    "Испания": "spain", "Италия": "italy", "Мексика": "mexico", "Индия": "india",
    "Шри-Ланка": "sri-lanka", "Тунис": "tunisia", "Индонезия": "indonesia",
    "Вьетнам": "vietnam", "Куба": "cuba", "Израиль": "israel", "Доминикана": "dominicana",
    "ОАЭ": "uae", "Кипр": "cyprus", "Таиланд": "thailand", "Египет": "egypt",
    "Турция": "turkey", "Китай": "china", "Танзания": "tanzania", "Маврикий": "mauritius",
    "Сейшелы": "seychelles", "Мальдивы": "maldives"
}

def clean_text(text):
    # Rule 93: Удаление SEO
    return re.sub(r'(Купить (тур|путевку)|Турагентство).*?(в|по|Москве|Подольск).*', '', text, flags=re.IGNORECASE).strip()

def is_header(line):
    line = line.strip()
    if not line or len(line) < 3: return False
    # 1. Если всё капсом - точно заголовок
    if line.isupper() and len(line) > 4: return True
    # 2. Если короткая строка без знака препинания в конце - скорее всего заголовок
    if len(line) < 60 and line[-1] not in '.,;:!?)': return True
    return False

def render_file(txt_path):
    if not os.path.exists(txt_path): return
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines()]

    if not lines: return

    meta = {'name': '', 'hero': '', 'is_memo': False}
    content = []
    is_body = False
    
    # Парсинг заголовка
    first_line = lines[0]
    if "ПАМЯТКА" in first_line:
        meta['is_memo'] = True
        meta['name'] = first_line.split(":", 1)[1].strip() if ":" in first_line else first_line
    elif "СТРАНА:" in first_line:
        meta['name'] = first_line.split(":", 1)[1].strip()
    else:
        meta['name'] = first_line

    for l in lines:
        if l.startswith("HERO_PHOTO:"): meta['hero'] = l.split(":", 1)[1].strip()
        elif "КОНТЕНТ" in l: is_body = True
        elif is_body: content.append(l)

    rendered = []
    current_reg = False
    
    for i, l in enumerate(content):
        l = clean_text(l)
        if not l: continue
        
        detect_header = False
        header_title = ""
        
        if l.startswith("РЕГИОН:"):
            detect_header = True
            header_title = l.replace("РЕГИОН:", "").strip()
        elif meta['is_memo'] and is_header(l):
            detect_header = True
            header_title = l.capitalize() if not l.isupper() else l

        if detect_header:
            if current_reg: rendered.append('</div></section>')
            rendered.append(f'<section class="pt-24 border-t border-black/5"><h2 class="text-6xl font-black mb-16 tracking-tight">{header_title}</h2><div class="space-y-8">')
            current_reg = True
        elif l.startswith("ФОТО:"):
            img = l.replace("ФОТО:", "").strip()
            cls = "w-full h-[500px] object-cover rounded-[3rem] shadow-xl mb-4" if current_reg else "w-full h-[60vh] object-cover rounded-[3rem] shadow-2xl mb-12"
            rendered.append(f'<img src="{img}" class="{cls}" loading="lazy">')
        else:
            if l.lower() == meta['name'].lower(): continue
            
            # Определяем стиль: списки должны стоять плотнее
            is_bullet = any(l.startswith(c) for c in "●•-*")
            
            # Если это пункт списка, убираем огромный нижний отступ
            margin_cls = "mb-2" if is_bullet else "mb-8"
            text_size = "text-xl" if is_bullet else "text-2xl"
            
            rendered.append(f'<p class="{text_size} leading-relaxed text-on-surface-variant font-light {margin_cls}">{l}</p>')
            
    if current_reg: rendered.append('</div></section>')

    # Сборка
    template_path = "template.html"
    if not os.path.exists(template_path): return
    
    with open(template_path, "r", encoding='utf-8') as f: html_tpl = f.read()
    
    name_for_slug = meta['name'].replace("Памятка_", "").replace("Памятка ", "").strip()
    slug = SLUGS.get(name_for_slug, name_for_slug.lower())
    
    title = f"Памятка: {meta['name']}" if meta['is_memo'] else meta['name']
    res = html_tpl.replace("██Название страны██", title).replace("██Название██", title)
    res = res.replace("██hero.jpg██", meta['hero']).replace("██Страна██", meta['name'])
    res = res.replace("PAGE_COUNTRY", meta['name'])
    res = res.replace("██slug██", slug)
    res = res.replace("<!-- Контент здесь -->", "\n".join(rendered))
    
    pdf_btn = ""
    if meta['is_memo']:
        pdf_btn = '<button id="download-pdf-btn" onclick="downloadPDF()" class="inline-block bg-black text-white px-10 py-4 rounded-full text-lg font-bold shadow-lg hover:scale-105 active:scale-95 transition-all flex items-center gap-2"><span class="material-symbols-outlined">download</span> Скачать PDF</button>'
        res = re.sub(r'<a href="memo-.*?class=".*?">Памятка туристу</a>', '', res)
    
    res = res.replace("<!-- PDF_BUTTON_PLACEHOLDER -->", pdf_btn)

    # Имя файла
    prefix = "memo-" if meta['is_memo'] else ""
    out_name = f"{prefix}{slug}.html"
    
    with open(out_name, "w", encoding='utf-8') as f: f.write(res)
    print(f"✅ Готово: {out_name}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        files = glob.glob("content_extracted/*.txt")
        print(f"🚀 Найдено файлов: {len(files)}. Начинаю сборку...")
        for f in files: render_file(f)
        print("✨ ВСЕ ФАЙЛЫ ЗАВЕРСТАНЫ!")
    elif len(sys.argv) > 1:
        render_file(sys.argv[1])
    else:
        print("Используй: python zero_loss_render.py --all")
