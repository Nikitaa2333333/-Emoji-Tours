import os
import re

def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # 1. Сначала исправляем "Паспортный контроль"
    p_control_pattern = re.compile(r'<(p|h2|div)[^>]*>(?:\s*|<strong>)*Паспортный\s+контроль\.\s+Виза\.?(?:\s*|</strong>)*</\1>', re.IGNORECASE | re.DOTALL)
    if p_control_pattern.search(content):
        print(f"  - Исправляем 'Паспортный контроль' в {filename}")
        new_header = '<section class=\"pt-12 border-t border-black/5\">\n                        <h2 id=\"section-pasportnyj-kontrol-viza\" class=\"text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none\">Паспортный контроль. Виза</h2>\n                        <div class=\"space-y-6\">'
        content = p_control_pattern.sub(new_header, content)
        changed = True

    # 2. УМНЫЙ ЗАГОЛОВОК: "По прилете в аэропорт..."
    # Ищем начало любого параграфа, которое начинается с "По прилете в аэропорт"
    # Мы выделяем только фразу "По прилете в аэропорт [Страны]"
    pattern = re.compile(r'(<p[^>]*>)(\s*По\s+прилете\s+в\s+аэропорт\s+[^<\s,]+(?:\s+[^<\s,]+)?)(.*?)(</p>)', re.IGNORECASE | re.DOTALL)
    
    match = pattern.search(content)
    if match:
        full_p_tag = match.group(0)
        p_start = match.group(1)
        arrival_header_text = match.group(2).strip()
        rest_of_text = match.group(3).strip()
        p_end = match.group(4)
        
        # Если это уже заголовок или внутри заголовка, пропускаем
        if 'class=\"text-4xl' in full_p_tag or '<h2' in full_p_tag:
            pass
        else:
            print(f"  - Разрезаем параграф и создаем заголовок '{arrival_header_text}' в {filename}")
            anchor_id = "section-arrival-airport"
            
            # Собираем новую структуру: Секция -> H2 -> Открытый DIV со следующим текстом
            new_structure = f'<section class=\"pt-12 border-t border-black/5\">\n                        <h2 id=\"{anchor_id}\" class=\"text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none\">{arrival_header_text}</h2>\n                        <div class=\"space-y-6\">\n                            <p class=\"text-lg md:text-xl leading-relaxed text-black font-normal mb-8\">{rest_of_text}</p>'
            
            content = content.replace(full_p_tag, new_structure)
            changed = True
            
            # Добавляем в навигацию (sidebar)
            nav_pattern = re.compile(r'(<nav[^>]*id=\"sidebar-nav\"[^>]*>.*?<ul[^>]*>)', re.DOTALL)
            if anchor_id not in content:
                nav_link = f'\n                    <li><a href=\"#{anchor_id}\" class=\"nav-link block py-2 text-base font-medium text-black/60 hover:text-black transition-colors\">По прилете в аэропорт</a></li>'
                content = nav_pattern.sub(r'\1' + nav_link, content)

    if changed:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

files = [f for f in os.listdir('.') if f.startswith('memo-') and f.endswith('.html')]
for f in files:
    if process_file(f):
        print(f"  - Файл {f} успешно обновлен.")
    else:
        # print(f"  - В файле {f} ничего не найдено.")
        pass
