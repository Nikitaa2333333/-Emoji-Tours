import os
import re

def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # 1. ТЕКСТ -> ЗАГОЛОВОК: "Паспортный контроль. Виза."
    # Ищем p, h2 или div, содержащий эту фразу
    p_control_pattern = re.compile(r'<(p|h2|div)[^>]*>(?:\s*|<strong>)*Паспортный\s+контроль\.\s+Виза\.?(?:\s*|</strong>)*</\1>', re.IGNORECASE | re.DOTALL)
    if p_control_pattern.search(content):
        print(f"  - Исправляем заголовок 'Паспортный контроль' в {filename}")
        new_header = '<section class=\"pt-12 border-t border-black/5\">\n                        <h2 id=\"section-pasportnyj-kontrol-viza\" class=\"text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none\">Паспортный контроль. Виза</h2>\n                        <div class=\"space-y-6\">'
        content = p_control_pattern.sub(new_header, content)
        changed = True

    # 2. ТЕКСТ -> ЗАГОЛОВОК: "По прилете в аэропорт [Страны]"
    # Ищем абзац, который начинается с этих слов
    arrival_pattern = re.compile(r'<p[^>]*>(\s*По\s+прилете\s+в\s+аэропорт\s+[^<\s]+(?:\s+[^<\s]+)?)(?:\s+необходимо[^<]*)?</p>', re.IGNORECASE | re.DOTALL)
    
    # Чтобы не сломать предложение, мы ищем именно короткие заголовки или начало текста
    # Но на скриншоте это выглядит как отдельная строка.
    # Попробуем найти конкретно предложение, которое нужно выделить.
    
    match = arrival_pattern.search(content)
    if match:
        full_text = match.group(1).strip()
        print(f"  - Создаем заголовок '{full_text}' в {filename}")
        anchor_id = "section-arrival-airport"
        new_arrival_section = f'<section class=\"pt-12 border-t border-black/5\">\n                        <h2 id=\"{anchor_id}\" class=\"text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none\">{full_text}</h2>\n                        <div class=\"space-y-6\">'
        content = arrival_pattern.sub(new_arrival_section, content)
        changed = True
        
        # Добавляем в навигацию
        nav_pattern = re.compile(r'(<nav[^>]*id=\"sidebar-nav\"[^>]*>.*?<ul[^>]*>)', re.DOTALL)
        if anchor_id not in content:
            nav_link = f'\n                    <li><a href=\"#{anchor_id}\" class=\"nav-link block py-2 text-base font-medium text-black/60 hover:text-black transition-colors\">{full_text}</a></li>'
            content = nav_pattern.sub(r'\1' + nav_link, content)

    if changed:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

files = [f for f in os.listdir('.') if f.startswith('memo-') and f.endswith('.html')]
for f in files:
    if process_file(f):
        print(f"Файл {f} успешно обновлен.")
    else:
        print(f"В файле {f} ничего не найдено.")
