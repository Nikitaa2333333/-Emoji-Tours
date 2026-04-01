import os
import re

def fix_responsive_issues(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Исправление горизонтального скролла (CSS)
    # Ищем блок стилей и добавляем overflow-x: hidden
    if '<style>' in content:
        # Исправляем стили body
        content = re.sub(r'(body\s*\{[^\}]*)(\})', r'\1 overflow-x: hidden; width: 100%; \2', content)
        # Исправляем стили html
        content = re.sub(r'(html\s*\{[^\}]*)(\})', r'\1 overflow-x: hidden; \2', content)

    # 2. Исправление обрезки изображений (превращаем фиксированную высоту в h-auto на мобилках)
    
    # Регулярка для замены h-[...] на h-auto md:h-[...]
    # И rounded-[...] на rounded-[2rem] md:rounded-[...]
    
    # Список паттернов классов для замены
    replacements = [
        # Основные фото регионов (1 шт)
        ('w-full h-[500px] object-cover rounded-[3rem] shadow-xl mb-4', 
         'w-full h-auto md:h-[500px] object-cover rounded-[2rem] md:rounded-[3rem] shadow-xl mb-4'),
        
        ('w-full h-[400px] object-cover rounded-[2.5rem] shadow-lg',
         'w-full h-auto md:h-[400px] object-cover rounded-[2rem] md:rounded-[2.5rem] shadow-lg'),
        
        ('w-full h-[55vh] object-cover rounded-[2.5rem] shadow-xl',
         'w-full h-auto md:h-[55vh] object-cover rounded-[2rem] md:rounded-[2.5rem] shadow-xl'),

        # Двойные фото (сетка 2 колонки -> 1 на мобиле)
        ('grid grid-cols-2 gap-6', 'grid grid-cols-1 md:grid-cols-2 gap-6'),
        ('h-72 rounded-[2rem]', 'h-auto md:h-72 object-cover rounded-[2rem]'),
        
        # Общий фикс для object-cover с фиксированной высотой (чтобы h-auto не ломался)
        ('class="w-full h-72 object-cover rounded-[2rem]"', 'class="w-full h-auto md:h-72 object-cover rounded-[2rem]"')
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Проходим по всем HTML файлам в текущей директории
html_files = [f for f in os.listdir('.') if f.endswith('.html')]

print(f"Обработка {len(html_files)} файлов...")
for filename in html_files:
    print(f"Фикс: {filename}")
    fix_responsive_issues(filename)

print("Готово! Все страницы адаптированы.")
