import os
import glob
import re

def fix_html_layout(file_path):
    print(f"Обработка {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Исправляем обрезку H1 и H2 (leading-none -> leading-[1.1])
    # Добавляем небольшой запас сверху для H1, чтобы он не слипался с шапкой
    content = content.replace('leading-none mb-8', 'leading-[1.1] pt-6 mb-10')
    
    # 2. Убираем "дырки" на памятках (вертикальные)
    # Находим контейнер контента и уменьшаем огромный space-y-16
    content = content.replace('space-y-16" id="memo-content-area"', 'space-y-8" id="memo-content-area"')
    
    # 3. Уменьшаем отступ первой секции, чтобы не было дырки под кнопками
    # Находим первый <section class="pt-12" внутри memo-content-area
    regex_first_section = re.compile(r'(<div[^>]*id="memo-content-area"[^>]*>\s*)<section class="pt-12', re.DOTALL)
    content = regex_first_section.sub(r'\1<section class="pt-4', content)

    # 4. Оптимизируем поля на мобилках (px-8 -> px-6)
    # Это сделает текст шире на узких экранах
    content = content.replace('px-8 relative flex flex-col', 'px-5 md:px-8 relative flex flex-col')

    # 5. Очистка от "завалов" лишних </div>
    # Обычно после основного контента идет блок с кнопками или просто закрытие секций
    # Мы ищем место перед <!-- ═══ ФОРМА или перед <footer>
    content = re.sub(r'(</div>\s*){4,}(?=\s*(?:<!-- ═══ ФОРМА|<footer>))', '</div>\n        </div>\n', content, flags=re.DOTALL)

    # 6. Исправляем двойные атрибуты и опечатки
    content = content.replace('id="section-о-стране" id="section-о-стране"', 'id="section-о-стране"')
    
    # 7. Дополнительно: исправим leading у H2 (они тоже могут задевать границы)
    content = content.replace('class="text-6xl font-black mb-8 tracking-tight"', 'class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1]"')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

# Список всех файлов для обработки (страны и памятки)
html_files = glob.glob("*.html")
targets = [f for f in html_files if f not in ["index.html"]]

for file in targets:
    fix_html_layout(file)

# Не забываем обновить template.html, чтобы новые страницы были сразу нормальными
if os.path.exists("template.html"):
    fix_html_layout("template.html")

print("\n✨ Готово! Все макеты исправлены. Теперь заголовки не режутся, а дырки на полях исчезли.")
