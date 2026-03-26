import os
import re
import html
import shutil

# Директории
BASE_DIR = r"c:\Users\User\Downloads\tilda dododo\raw_tilda\emojitours.ru"
IMAGES_SRC = os.path.join(BASE_DIR, "images")
OUTPUT_DIR = r"c:\Users\User\Downloads\tilda dododo\content_extracted"
PROJECT_ROOT = r"c:\Users\User\Downloads\tilda dododo"
LOCAL_IMAGES_DIR = os.path.join(PROJECT_ROOT, "images")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

if not os.path.exists(LOCAL_IMAGES_DIR):
    os.makedirs(LOCAL_IMAGES_DIR)

# Полная база маппинга
MAPPING = {
    "page4325707.html": "Испания",
    "page4217266.html": "Италия",
    "page4200612.html": "Мексика",
    "page4160212.html": "Индия",
    "page4157617.html": "Шри-Ланка",
    "page4138132.html": "Тунис",
    "page4110612.html": "Индонезия",
    "page4083492.html": "Вьетнам",
    "page4077378.html": "Куба",
    "page4074949.html": "Израиль",
    "page4057808.html": "Доминикана",
    "page4048301.html": "ОАЭ",
    "page4037335.html": "Кипр",
    "page4031511.html": "Таиланд",
    "page4027787.html": "Египет",
    "page4020107.html": "Турция",
    "page127624096.html": "Китай",
    "page127411046.html": "Танзания",
    "page127101246.html": "Маврикий",
    "page126780916.html": "Сейшелы",
    "page126512346.html": "Мальдивы",
}

# Связь Страна -> Файл памятки
COUNTRY_TO_MEMO = {
    "Мексика": "page4684488.html",
    "Индия": "page4176573.html",
    "Куба": "page4078918.html",
    "Израиль": "page4075671.html",
    "Доминикана": "page4065279.html",
    "ОАЭ": "page4055362.html",
    "Кипр": "page4046944.html",
    "Турция": "page4020740.html",
    "Шри-Ланка": "page128475226.html",
    "Тунис": "page128482946.html",
    "Индонезия": "page128442426.html",
    "Вьетнам": "page128405116.html",
    "Таиланд": "page128325586.html",
    "Египет": "page128281366.html",
    "Китай": "page127635086.html",
    "Танзания": "page127414696.html",
    "Маврикий": "page127119236.html",
    "Сейшелы": "page126804106.html",
    "Мальдивы": "page126520756.html",
}

def clean_text(text):
    # Убираем HTML-сущности
    text = html.unescape(text)
    
    # Пытаемся сохранить жирность из span с inline стилями Tilda
    text = re.sub(r'<span[^>]*style="[^"]*font-weight:\s*(?:700|bold)[^"]*"[^>]*>(.*?)</span>', r'<b>\1</b>', text, flags=re.IGNORECASE)
    # Унифицируем strong -> b
    text = re.sub(r'</?(?:strong|b)>', '<b>', text, flags=re.IGNORECASE)
    text = re.sub(r'<b>\s*</b>', '', text) # чистим пустые
    
    # Заменяем блочные теги на переносы строк до удаления всех тегов
    text = re.sub(r'<(br|p|div|li|h[1-6])[^>]*>', '\n', text, flags=re.IGNORECASE)
    
    # Убираем все остальные теги КРОМЕ <b> и <i>
    text = re.sub(r'<(?!/?(?:b|i)\b)[^>]+>', '', text)
    
    # Убираем SEO-рекламу из gemini.md
    text = re.sub(r'Купить (путевку|тур|путешествие).*?(в|по) .*? (Подольске|Щербинке|Москве|Подольск|Щербинка|Москва)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Турагентство (Подольск|Щербинка|Москва)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'купить тур в .*? (Подольск|Москва|Щербинка)', '', text, flags=re.IGNORECASE)
    
    # Очищаем пустые строки и лишние пробелы в строках, но сохраняем структуру строк
    lines = [line.strip() for line in text.split('\n')]
    result_lines = []
    for line in lines:
        if line:
            result_lines.append(line)
        elif result_lines and result_lines[-1] != "":
            result_lines.append("")
            
    return '\n'.join(result_lines).strip()

def process_file(filename, country_name, is_memo=False):
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath): return ""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Извлекаем контент внутри allrecords
    all_recs = re.search(r'<div id="allrecords".*?>(.*?)<!--/allrecords-->', content, re.DOTALL)
    recs_text = all_recs.group(1) if all_recs else content

    # Шаблон для сбора всех полей по порядку
    pattern = re.compile(r'(field="(?:title|text|descr)"[^>]*?>(.*?)</(?:div|h[1-6])>|data-original="(.*?)")', re.DOTALL)
    
    output = []
    if is_memo:
        output.append(f"ПАМЯТКА ТУРИСТА: {country_name}")
    else:
        output.append(f"СТРАНА: {country_name}")
        memo_file = COUNTRY_TO_MEMO.get(country_name)
        if memo_file:
            memo_txt_name = f"Памятка_{country_name.replace(' ', '_')}.txt"
            output.append(f"MEMO_LINK: {memo_txt_name}")
    
    output.append(f"SOURCE_HTML: {filename}")
    
    hero_match = re.search(r'data-content-cover-bg="(.*?)"', content)
    if hero_match:
        img_name = os.path.basename(hero_match.group(1))
        output.append(f"HERO_PHOTO: {img_name}")
        
        # МАГИЯ КОПИРОВАНИЯ:
        src_path = os.path.join(IMAGES_SRC, img_name)
        if os.path.exists(src_path):
            shutil.copy2(src_path, os.path.join(PROJECT_ROOT, img_name)) # в корень для страниц стран
            shutil.copy2(src_path, os.path.join(LOCAL_IMAGES_DIR, img_name)) # в /images/ для главной
    
    output.append("\nКОНТЕНТ (ТЕКСТ И ФОТО):")
    
    for match in pattern.finditer(recs_text):
        if match.group(1) and match.group(2) is not None: # Текст (с проверкой на наличие контента)
            txt = clean_text(match.group(2))
            if txt and len(txt) > 2:
                # Если это не название страны, это либо регион, либо параграф
                if not is_memo and len(txt) < 50 and txt.lower() not in country_name.lower():
                    output.append(f"\nРЕГИОН: {txt}")
                else:
                    output.append(f"\n{txt}\n")
        elif match.group(3): # Фото
            img = os.path.basename(match.group(3))
            if img and not (img.endswith('.png') or img.endswith('.svg')): # фильтруем иконки
                output.append(f"ФОТО: {img}")
                
                # МАГИЯ КОПИРОВАНИЯ:
                src_path = os.path.join(IMAGES_SRC, img)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, os.path.join(PROJECT_ROOT, img)) # в корень для страниц стран
                    shutil.copy2(src_path, os.path.join(LOCAL_IMAGES_DIR, img)) # в /images/ для главной

    return '\n'.join(output)

    return '\n'.join(output)

# 1. Сбор стран
print("Collecting countries and linking memos...")
summary = ["ТАБЛИЦА ВСЕХ СТРАН И ПАМЯТОК:\n"]

for f, name in MAPPING.items():
    text = process_file(f, name)
    out_name = f"{name.replace(' ', '_')}.txt"
    with open(os.path.join(OUTPUT_DIR, out_name), 'w', encoding='utf-8') as out:
        out.write(text)
    
    memo_file = COUNTRY_TO_MEMO.get(name)
    memo_status = f"Памятка: Памятка_{name.replace(' ', '_')}.txt" if memo_file else "БЕЗ ПАМЯТКИ"
    summary.append(f"{name:15} | {memo_status}")

# 2. Сбор памяток
for name, f in COUNTRY_TO_MEMO.items():
    text = process_file(f, name, is_memo=True)
    out_name = f"Памятка_{name.replace(' ', '_')}.txt"
    with open(os.path.join(OUTPUT_DIR, out_name), 'w', encoding='utf-8') as out:
        out.write(text)

# Сохраняем сводку
with open(os.path.join(OUTPUT_DIR, "_summary_map.txt"), 'w', encoding='utf-8') as f:
    f.write('\n'.join(summary))

print(f"\nDONE! Created {len(MAPPING)} country files and {len(COUNTRY_TO_MEMO)} memo files.")
print(f"Check _summary_map.txt for the full list.")
