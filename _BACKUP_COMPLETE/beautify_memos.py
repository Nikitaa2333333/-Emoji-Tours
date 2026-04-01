import os
import re
import glob

def slugify(text):
    text = text.lower()
    mapping = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z','и':'i','й':'j','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'c','ч':'ch','ш':'sh','щ':'sch','ь':'','ы':'y','ъ':'','э':'e','ю':'yu','я':'ya'
    }
    for k, v in mapping.items():
        text = text.replace(k, v)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def fix_acronyms(text):
    acronyms = {
        'рф': 'РФ',
        'рсa': 'РСА',
        'кнр': 'КНР',
        'оаэ': 'ОАЭ',
        'сша': 'США',
        'ес': 'ЕС',
        'вип': 'VIP',
        'пцр': 'ПЦР'
    }
    for low, high in acronyms.items():
        # Заменяем только если это отдельное слово
        text = re.sub(rf'\b{low}\b', high, text, flags=re.IGNORECASE)
    return text

def beautify_html(content):
    # 0. Удаление мусорных секций (футерные фразы, пустые символы)
    kill_patterns = [
        r'<section[^>]*>\s*<h2[^>]*>\s*/\s*</h2>\s*</section>',
        r'<section[^>]*>\s*<h2[^>]*>\s*Индивидуальный предприниматель.*?\s*</h2>\s*</section>',
        r'<section[^>]*>\s*<h2[^>]*>\s*E-mail:.*?\s*</h2>\s*</section>',
        r'<section[^>]*>\s*<h2[^>]*>\s*Соцсети:.*?\s*</h2>\s*</section>',
        r'<section[^>]*>\s*<h2[^>]*>\s*Желаем вам приятного путешествия.*?</h2>\s*</section>'
    ]
    for pattern in kill_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)

    # 1. Заголовки H1: Название страны в спан
    def fix_h1(match):
        attrs = match.group(1)
        text = match.group(2)
        if 'Памятка:' in text:
            parts = text.split(':', 1)
            text = f'Памятка: <span class="text-primary">{parts[1].strip()}</span>'
        return f'<h1{attrs}>{text}</h1>'
    content = re.sub(r'<h1([^>]*)>(.*?)</h1>', fix_h1, content, flags=re.DOTALL)

    # 2. Очистка H2 от буллитов и фикс регистра
    def clean_h2(match):
        attrs = match.group(1)
        text = match.group(2)
        # Убираем ●
        text = text.replace('●', '').strip()
        # Фикс регистра
        if text.isupper():
            text = text.capitalize()
        elif text and text[0].islower():
            text = text[0].upper() + text[1:]
        # Фикс аббревиатур
        text = fix_acronyms(text)
        return f'<h2{attrs}>{text}</h2>'
    content = re.sub(r'<h2([^>]*)>(.*?)</h2>', clean_h2, content, flags=re.DOTALL)

    # 3. Буллиты в тексте: Заменяем ● на красивые иконки
    bullet_pattern = r'<p class="([^"]*)">●\s*(.*?)</p>'
    def fix_bullet(match):
        classes = match.group(1)
        text = match.group(2)
        clean_classes = re.sub(r'mb-\d+', '', classes).strip()
        return f'''
<div class="group flex items-start gap-5 mb-6 transition-all hover:translate-x-2">
    <div class="mt-1 flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-black transition-colors">
        <span class="material-symbols-outlined text-[20px]">check</span>
    </div>
    <p class="{clean_classes} pt-1">{text}</p>
</div>'''
    content = re.sub(bullet_pattern, fix_bullet, content)

    # 4. Хайлайты (Внимание, Важно)
    highlight_map = {
        r"Внимание!?": {"icon": "warning", "label": "Внимание"},
        r"Важно!?": {"icon": "info", "label": "Важно знать"},
        r"Запрещено!?": {"icon": "block", "label": "Это запрещено"},
        r"Обращаем внимание": {"icon": "priority_high", "label": "Обратите внимание"}
    }
    for word_regex, info in highlight_map.items():
        pattern = rf'<p class="([^"]*font-light[^"]*)">({word_regex})(.*?)</p>'
        def fix_highlight(match):
            classes = match.group(1)
            rest = match.group(3).strip()
            rest = re.sub(r'^[:\s]+', '', rest)
            if not rest: return match.group(0) # Не трогаем пустые
            return f'''
<div class="bg-primary/5 border-l-8 border-primary p-10 rounded-r-[3rem] my-16 shadow-inner">
    <div class="flex items-center gap-4 mb-6">
        <div class="w-12 h-12 rounded-2xl bg-primary flex items-center justify-center shadow-lg">
            <span class="material-symbols-outlined text-black text-2xl font-bold">{info["icon"]}</span>
        </div>
        <span class="font-black uppercase tracking-widest text-sm text-black/60">{info["label"]}</span>
    </div>
    <p class="{classes} text-black font-medium leading-relaxed">{rest}</p>
</div>'''
        content = re.sub(pattern, fix_highlight, content, flags=re.IGNORECASE)

    # 5. Экстренные телефоны (Special Block)
    # Ищем H2 которые содержат "полиция", "пожарные", "скорая" или числовые номера
    def fix_emergency(match):
        section_id = match.group(1)
        text = match.group(3).strip()
        if any(w in text.lower() for w in ["полиция", "пожарная", "скорая", "экстренн"]):
            # Оборачиваем в супер-карточку
            return f'''
<div class="bg-red-50 border-2 border-red-500/20 p-12 rounded-[3.5rem] my-20 relative overflow-hidden group">
    <div class="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-125 transition-transform duration-700">
        <span class="material-symbols-outlined text-9xl text-red-600">emergency</span>
    </div>
    <div class="relative z-10">
        <div class="flex items-center gap-4 mb-8">
            <span class="w-3 h-3 rounded-full bg-red-500 animate-pulse"></span>
            <span class="font-black uppercase tracking-widest text-red-600">Срочная помощь</span>
        </div>
        <h2 id="{section_id}" class="text-5xl font-black text-red-950 mb-4">{text}</h2>
        <p class="text-red-900/60 font-medium">Рекомендуем сохранить этот номер в контактах телефона</p>
    </div>
</div>'''
        return match.group(0)
    content = re.sub(r'<h2 id="([^"]*)" class="[^"]*">(.*?)</h2>', fix_emergency, content, flags=re.DOTALL)

    # 6. Контакты Посольств
    embassy_sections = re.findall(r'(<section[^>]*>(?:(?!</section>).)*?Посольство.*?/section>)', content, re.DOTALL | re.IGNORECASE)
    for section in embassy_sections:
        h2_match = re.search(r'<h2 id="([^"]*)".*?>(.*?)</h2>', section, re.DOTALL)
        if h2_match:
            sid = h2_match.group(1)
            title = fix_acronyms(h2_match.group(2).strip())
            inner_content = re.sub(r'<h2[^>]*>.*?</h2>', '', section, flags=re.DOTALL)
            inner_content = inner_content.replace('font-light', 'font-normal')
            
            card_html = f'''
<section class="pt-24 border-t border-black/5">
    <div class="flex items-center gap-4 mb-12">
        <div class="w-2 h-12 bg-primary rounded-full"></div>
        <h2 id="{sid}" class="text-5xl font-black">{title}</h2>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="bg-white/50 backdrop-blur-sm p-10 rounded-[2.5rem] border border-black/5 shadow-sm hover:shadow-xl transition-all duration-500">
            {inner_content}
        </div>
        <div class="relative overflow-hidden rounded-[2.5rem] bg-primary/10 flex items-center justify-center group">
            <span class="material-symbols-outlined text-8xl text-primary/20 group-hover:scale-110 transition-transform duration-700">account_balance</span>
        </div>
    </div>
</section>
'''
            content = content.replace(section, card_html)

    # 7. Сайдбар: Синхронизируем ссылки
    h2_matches = re.finditer(r'<h2 id="([^"]*)".*?>(.*?)</h2>', content)
    nav_links = ""
    for match in h2_matches:
        text = re.sub(r'<[^>]+>', '', match.group(2)).strip()
        if not text: continue
        nav_links += f'<a href="#{match.group(1)}" class="nav-link">{text}</a>\n'

    content = re.sub(r'<nav id="quick-links"[^>]*>.*?</nav>', f'<nav id="quick-links" class="flex flex-col border-l border-black/5">{nav_links}</nav>', content, flags=re.DOTALL)

    return content

def main():
    files = glob.glob("memo-*.html")
    for file_path in files:
        print(f"Beautifying {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = beautify_html(content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

if __name__ == "__main__":
    main()
