import os
import re

# Самый полный список заголовков для H2 (попадают в меню)
VALID_HEADERS_H2 = [
    "Перед отъездом", "Собирая багаж", "В Российском аэропорту", "Таможенный контроль",
    "Санитарный контроль", "Ветеринарный контроль", "Регистрация на рейс", 
    "Пограничный контроль", "Внимание", "Посольство", "Консульство", "Экстренные телефоны",
    "Время", "Климат", "Валюта", "Язык", "Население", "Религия", "Обычаи", 
    "Транспорт", "Телефон", "В отеле", "Напряжение электросети", "Экскурсии", 
    "Кухня", "Магазины", "Виза", "Связь", "Деньги", "Погода", "О стране",
    "Полезная информация", "Праздники", "Личная гигиена", "Безопасность",
    "В случае потери паспорта", "Посольство РФ", "Беременным женщинам",
    "Трансфер", "Медицинская помощь", "Электричество", "Важные контакты", 
    "Аэропорт", "Обмен валюты", "Чаевые", "Особенности отеля", "Power Bank",
    "В аэропорту", "Дьюти-фри", "Такси", "По прилете", "Памятка туристу",
    "Памятка по стране", "Важные телефоны", "Паспортный контроль"
]

# Список слов для H3 (подзаголовки внутри разделов)
VALID_HEADERS_H3 = [
    "Адрес", "Телефоны", "Консульский отдел", "Электронная почта", "Факс",
    "Время работы", "Как добраться", "Местная сим-карта", "Где менять",
    "Чаевые в ресторанах", "Особенности климата", "Правила поведения",
    "Экстренный телефон", "Полиция", "Справочная", "Пожарная служба",
    "Скорая помощь", "Интернет", "Паспортный контроль", "Курс валют",
    "Правила личной гигиены", "Безопасность", "Важно", "Кратко", "Примечание"
]

def translit(text):
    cyr = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя '
    lat = 'abvgdeezzijklmnoprstufhzcss_y_eua_'
    table = str.maketrans(cyr, lat)
    text = text.lower().translate(table)
    return re.sub(r'[^a-z0-9_-]', '', text).strip()

def fix_memo(filepath):
    print(f"--- Обработка {filepath} ---")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Сначала ищем потенциальные H3 (подзаголовки)
    # Ищем короткие абзацы с классами text-xl или font-bold/black
    def to_h3(match):
        text = match.group(1).strip()
        clean_text = re.sub('<[^>]*>', '', text).strip()
        
        # Если это что-то из списка H3 или короткое с двоеточием
        is_h3 = False
        if any(v.lower() in clean_text.lower() for v in VALID_HEADERS_H3) and len(clean_text) < 60:
            is_h3 = True
        elif len(clean_text) < 40 and clean_text.endswith(':'):
            is_h3 = True
            
        if is_h3:
            # Премиальный стиль H3: жирный, с золотой полоской
            return f'<h3 class="text-2xl font-black mt-12 mb-6 text-on-surface flex items-center gap-4"><span class="w-1.5 h-8 bg-primary rounded-full"></span>{text}</h3>'
        return match.group(0)

    # Применяем поиск H3
    content = re.sub(r'<p class="[^"]*(?:text-xl|font-black|font-bold)[^"]*">(.*?)</p>', to_h3, content)

    # 2. Теперь ищем H2 (Главные разделы)
    def to_h2(match):
        text = match.group(1).strip()
        clean_text = re.sub('<[^>]*>', '', text).strip()
        
        if any(v.lower() in clean_text.lower() for v in VALID_HEADERS_H2) and len(clean_text) < 80:
            header_id = "section-" + translit(clean_text)[:30]
            # H2 с бордером сверху (стиль памятки)
            return f'<section class="pt-12 border-t border-black/5"><h2 id="{header_id}" class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none">{text}</h2>'

    # Применяем поиск H2 среди тех, что еще P
    content = re.sub(r'<p class="[^"]*text-xl[^"]*">(.*?)</p>', to_h2, content)

    # 3. Добавляем ID всем существующим H2 (если вдруг потерялись)
    def ensure_id(match):
        full_tag = match.group(0)
        if 'id="' in full_tag: return full_tag
        text = match.group(1).strip()
        clean_text = re.sub('<[^>]*>', '', text).strip()
        header_id = "section-" + translit(clean_text)[:30]
        return f'<h2 id="{header_id}" class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none">{text}</h2>'
    
    content = re.sub(r'<h2[^>]*>(.*?)</h2>', ensure_id, content)

    # 4. ОБНОВЛЕНИЕ МЕНЮ (Sidebar)
    headings = re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', content, re.DOTALL)
    if headings:
        nav_links_html = ""
        for anchor_id, title in headings:
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            if len(clean_title) > 60: continue
            nav_links_html += f'                        <a href="#{anchor_id}" class="nav-link">{clean_title}</a>\n'

        aside_pattern = re.compile(r'(<aside[^>]*>.*?<p[^>]*>Содержание</p>\s*)\s*(<nav[^>]*>.*?</nav>|.*?)(?=\s*</div>\s*</div>\s*</aside>)', re.DOTALL)
        new_nav = f'<nav id="quick-links" class="flex flex-col border-l border-black/5">\n{nav_links_html}                        </nav>'
        if aside_pattern.search(content):
            content = aside_pattern.sub(r'\1' + new_nav, content)
            print(f"  ✅ Меню обновлено: {len(headings)} пунктов.")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

# Запуск по всем файлам
files = [f for f in os.listdir('.') if f.startswith('memo-') and f.endswith('.html')]
for f in files:
    try:
        if fix_memo(f):
            print(f"  🔥 Готово!")
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
